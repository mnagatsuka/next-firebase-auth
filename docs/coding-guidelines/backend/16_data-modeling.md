# 16. Data Modeling & Migrations (NoSQL)

This section covers **DynamoDB data modeling** using **single-table design** patterns. It includes **partition key (PK) and sort key (SK) design**, **Global Secondary Indexes (GSIs)**, **entity composition**, and **optimistic concurrency control**.

The approach emphasizes **efficient access patterns**, **cost optimization**, and **scalable NoSQL design** for the established tech stack.


## 1. Single-Table Design Principles

### Core Concepts

```python
# Single table structure for all entities
Table: main_table
├── PK (Partition Key): Identifies entity type and ID
├── SK (Sort Key): Defines entity relationships and hierarchy  
├── GSI1PK/GSI1SK: Alternative access patterns
├── GSI2PK/GSI2SK: Additional access patterns
└── Attributes: Entity-specific data

# Example entities in single table:
# Users: PK=user#123, SK=profile
# Orders: PK=user#123, SK=order#456  
# Products: PK=product#789, SK=details
```

### Key Design Patterns

```python
# Pattern 1: Entity + Metadata
user_item = {
    'pk': 'user#12345',
    'sk': 'profile',
    'entity_type': 'user',
    'user_id': '12345',
    'email': 'user@example.com',
    'name': 'John Doe',
    'created_at': '2024-01-01T00:00:00Z'
}

# Pattern 2: One-to-Many Relationships  
order_item = {
    'pk': 'user#12345',        # Same PK as user
    'sk': 'order#67890',       # Different SK for orders
    'entity_type': 'order',
    'order_id': '67890',
    'user_id': '12345',
    'amount': 99.99,
    'status': 'completed'
}

# Pattern 3: GSI for Alternative Access
email_lookup = {
    'pk': 'user#12345',
    'sk': 'profile',
    'gsi1pk': 'email#user@example.com',  # Email lookup
    'gsi1sk': 'user#12345',
    'gsi2pk': 'status#active',           # Status queries
    'gsi2sk': '2024-01-01#user#12345'    # Time-based sorting
}
```

**Rules:**

* Use single table for all related entities.
* Design PK/SK to support primary access patterns.
* Use GSIs for alternative access patterns.
* Include entity_type for filtering.


## 2. Partition Key (PK) & Sort Key (SK) Design

### Primary Key Patterns

```python
# User entities
PK = 'user#{user_id}'
SK = 'profile'                    # User profile
SK = 'settings'                   # User settings  
SK = 'subscription#{sub_id}'      # User subscriptions

# Order entities
PK = 'user#{user_id}'            # Group by user
SK = 'order#{order_id}'          # Specific order
SK = 'order#{timestamp}#{order_id}'  # Time-ordered

# Product entities  
PK = 'product#{product_id}'
SK = 'details'                   # Product details
SK = 'inventory#{location}'      # Inventory by location
SK = 'review#{review_id}'        # Product reviews

# System entities
PK = 'config'
SK = 'app_settings'              # Application config
SK = 'feature_flags'             # Feature toggles
```

### Access Pattern Examples

```python
# Repository implementation
class DynamoDBRepository:
    """Single-table DynamoDB repository."""
    
    async def get_user_profile(self, user_id: str) -> Optional[User]:
        """Get user profile."""
        response = await self.table.get_item(
            Key={'pk': f'user#{user_id}', 'sk': 'profile'}
        )
        return self._item_to_user(response.get('Item'))
    
    async def get_user_orders(self, user_id: str) -> List[Order]:
        """Get all orders for user."""
        response = await self.table.query(
            KeyConditionExpression=Key('pk').eq(f'user#{user_id}') &
                                  Key('sk').begins_with('order#')
        )
        return [self._item_to_order(item) for item in response['Items']]
    
    async def get_recent_orders(self, user_id: str, days: int = 30) -> List[Order]:
        """Get recent orders using sort key filtering."""
        cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        response = await self.table.query(
            KeyConditionExpression=Key('pk').eq(f'user#{user_id}') &
                                  Key('sk').begins_with('order#'),
            FilterExpression=Attr('created_at').gte(cutoff_date)
        )
        return [self._item_to_order(item) for item in response['Items']]
```

**Rules:**

* Use hierarchical PK structure: `entity_type#id`.
* Design SK to enable range queries and sorting.
* Group related entities with same PK.
* Use timestamps in SK for chronological ordering.


## 3. Global Secondary Indexes (GSIs)

### GSI Design Patterns

```python
# GSI1: Email lookup for users
GSI1PK = 'email#{email}'
GSI1SK = 'user#{user_id}'

# GSI2: Status-based queries
GSI2PK = 'status#{status}'
GSI2SK = '{timestamp}#{entity_type}#{id}'

# GSI3: Category-based product lookup
GSI3PK = 'category#{category}'
GSI3SK = 'product#{product_id}'
```

### Repository GSI Queries

```python
class DynamoDBRepository:
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email using GSI1."""
        response = await self.table.query(
            IndexName='GSI1',
            KeyConditionExpression=Key('gsi1pk').eq(f'email#{email}')
        )
        
        items = response.get('Items', [])
        if not items:
            return None
        
        return self._item_to_user(items[0])
    
    async def get_active_users(self, limit: int = 50) -> List[User]:
        """Get active users using GSI2."""
        response = await self.table.query(
            IndexName='GSI2',
            KeyConditionExpression=Key('gsi2pk').eq('status#active'),
            ScanIndexForward=False,  # Latest first
            Limit=limit
        )
        
        return [self._item_to_user(item) for item in response['Items']]
    
    async def get_products_by_category(self, category: str) -> List[Product]:
        """Get products by category using GSI3."""
        response = await self.table.query(
            IndexName='GSI3',
            KeyConditionExpression=Key('gsi3pk').eq(f'category#{category}')
        )
        
        return [self._item_to_product(item) for item in response['Items']]
```

**Rules:**

* Design GSIs for alternative access patterns.
* Use sparse indexes to save costs.
* Project only necessary attributes.
* Consider query patterns when designing GSI keys.


## 4. Entity Composition & Relationships

### Entity Mapping

```python
# Domain entity to DynamoDB item mapping
@dataclass
class User:
    """User domain entity."""
    id: str
    email: str
    name: str
    status: str
    created_at: datetime
    updated_at: datetime

class UserMapper:
    """Maps between User entity and DynamoDB items."""
    
    @staticmethod
    def to_item(user: User) -> Dict[str, Any]:
        """Convert User entity to DynamoDB item."""
        return {
            'pk': f'user#{user.id}',
            'sk': 'profile',
            'entity_type': 'user',
            'user_id': user.id,
            'email': user.email,
            'name': user.name,
            'status': user.status,
            'created_at': user.created_at.isoformat(),
            'updated_at': user.updated_at.isoformat(),
            # GSI attributes
            'gsi1pk': f'email#{user.email}',
            'gsi1sk': f'user#{user.id}',
            'gsi2pk': f'status#{user.status}',
            'gsi2sk': f'{user.created_at.isoformat()}#user#{user.id}'
        }
    
    @staticmethod
    def from_item(item: Dict[str, Any]) -> User:
        """Convert DynamoDB item to User entity."""
        return User(
            id=item['user_id'],
            email=item['email'],
            name=item['name'],
            status=item['status'],
            created_at=datetime.fromisoformat(item['created_at']),
            updated_at=datetime.fromisoformat(item['updated_at'])
        )
```

### Aggregate Root Pattern

```python
# Order aggregate with line items
@dataclass
class Order:
    """Order aggregate root."""
    id: str
    user_id: str
    status: str
    total_amount: float
    line_items: List[OrderLineItem]
    created_at: datetime

@dataclass
class OrderLineItem:
    """Order line item."""
    id: str
    product_id: str
    quantity: int
    price: float

class OrderMapper:
    """Maps Order aggregate to multiple DynamoDB items."""
    
    @staticmethod
    def to_items(order: Order) -> List[Dict[str, Any]]:
        """Convert Order to multiple DynamoDB items."""
        items = []
        
        # Order header item
        order_item = {
            'pk': f'user#{order.user_id}',
            'sk': f'order#{order.id}',
            'entity_type': 'order',
            'order_id': order.id,
            'user_id': order.user_id,
            'status': order.status,
            'total_amount': order.total_amount,
            'created_at': order.created_at.isoformat(),
            'gsi1pk': f'order#{order.id}',
            'gsi1sk': 'header'
        }
        items.append(order_item)
        
        # Line item items
        for line_item in order.line_items:
            line_item_dict = {
                'pk': f'user#{order.user_id}',
                'sk': f'order#{order.id}#item#{line_item.id}',
                'entity_type': 'order_line_item',
                'order_id': order.id,
                'line_item_id': line_item.id,
                'product_id': line_item.product_id,
                'quantity': line_item.quantity,
                'price': line_item.price,
                'gsi1pk': f'order#{order.id}',
                'gsi1sk': f'item#{line_item.id}'
            }
            items.append(line_item_dict)
        
        return items
```

**Rules:**

* Map domain entities to DynamoDB items consistently.
* Use aggregate patterns for complex entities.
* Include all GSI attributes in item structure.
* Maintain entity relationships through key design.


## 5. Optimistic Concurrency Control

### Version-Based Concurrency

```python
# Add version field to entities
@dataclass
class User:
    id: str
    email: str
    name: str
    version: int = 1  # Optimistic locking version
    created_at: datetime
    updated_at: datetime

class OptimisticLockRepository:
    """Repository with optimistic locking."""
    
    async def save(self, user: User) -> User:
        """Save user with optimistic locking."""
        current_time = datetime.utcnow()
        
        try:
            # For updates, increment version
            if hasattr(user, '_is_new') and not user._is_new:
                new_version = user.version + 1
                
                response = await self.table.put_item(
                    Item={
                        'pk': f'user#{user.id}',
                        'sk': 'profile',
                        'user_id': user.id,
                        'email': user.email,
                        'name': user.name,
                        'version': new_version,
                        'updated_at': current_time.isoformat()
                    },
                    ConditionExpression=Attr('version').eq(user.version)
                )
                
                user.version = new_version
                user.updated_at = current_time
            else:
                # New item
                await self.table.put_item(
                    Item=UserMapper.to_item(user),
                    ConditionExpression=Attr('pk').not_exists()
                )
            
            return user
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise ConcurrentModificationError(
                    f"User {user.id} was modified by another process"
                )
            raise
```

### Timestamp-Based Concurrency

```python
class TimestampLockRepository:
    """Repository using timestamp-based optimistic locking."""
    
    async def update_user(self, user_id: str, updates: Dict[str, Any], 
                         last_modified: datetime) -> User:
        """Update user with timestamp check."""
        current_time = datetime.utcnow()
        
        # Build update expression
        update_expression = "SET "
        expression_values = {}
        
        for key, value in updates.items():
            update_expression += f"{key} = :{key}, "
            expression_values[f":{key}"] = value
        
        update_expression += "updated_at = :updated_at"
        expression_values[":updated_at"] = current_time.isoformat()
        expression_values[":last_modified"] = last_modified.isoformat()
        
        try:
            response = await self.table.update_item(
                Key={'pk': f'user#{user_id}', 'sk': 'profile'},
                UpdateExpression=update_expression,
                ConditionExpression=Attr('updated_at').eq(':last_modified'),
                ExpressionAttributeValues=expression_values,
                ReturnValues='ALL_NEW'
            )
            
            return UserMapper.from_item(response['Attributes'])
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise ConcurrentModificationError(
                    f"User {user_id} was modified since {last_modified}"
                )
            raise
```

### Conditional Operations

```python
class ConditionalRepository:
    """Repository with conditional operations."""
    
    async def create_user_if_not_exists(self, user: User) -> User:
        """Create user only if email doesn't exist."""
        try:
            await self.table.put_item(
                Item=UserMapper.to_item(user),
                ConditionExpression=Attr('gsi1pk').not_exists()
            )
            return user
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise UserAlreadyExistsError(f"User with email {user.email} already exists")
            raise
    
    async def increment_login_count(self, user_id: str) -> int:
        """Atomically increment login count."""
        try:
            response = await self.table.update_item(
                Key={'pk': f'user#{user_id}', 'sk': 'profile'},
                UpdateExpression='ADD login_count :inc',
                ExpressionAttributeValues={':inc': 1},
                ReturnValues='UPDATED_NEW'
            )
            return response['Attributes']['login_count']
        except ClientError as e:
            if e.response['Error']['Code'] == 'ValidationException':
                # First login - initialize counter
                await self.table.update_item(
                    Key={'pk': f'user#{user_id}', 'sk': 'profile'},
                    UpdateExpression='SET login_count = :count',
                    ExpressionAttributeValues={':count': 1}
                )
                return 1
            raise
```

**Rules:**

* Use version numbers or timestamps for optimistic locking.
* Handle ConditionalCheckFailedException appropriately.
* Use atomic operations for counters and flags.
* Design conditional expressions for business rules.


## 6. Migration Strategies

### Schema Evolution

```python
# Migration patterns for NoSQL
class DataMigration:
    """Handle data migrations in DynamoDB."""
    
    async def migrate_user_schema_v2(self):
        """Migrate users to include new fields."""
        paginator = self.dynamodb.meta.client.get_paginator('scan')
        
        for page in paginator.paginate(
            TableName=self.table_name,
            FilterExpression=Attr('entity_type').eq('user') &
                           Attr('schema_version').not_exists()
        ):
            for item in page['Items']:
                # Add new fields with defaults
                await self.table.update_item(
                    Key={'pk': item['pk'], 'sk': item['sk']},
                    UpdateExpression='SET schema_version = :v, preferences = :prefs',
                    ExpressionAttributeValues={
                        ':v': 2,
                        ':prefs': {'theme': 'light', 'notifications': True}
                    }
                )

# Backward compatibility
class BackwardCompatibleMapper:
    """Handle multiple schema versions."""
    
    @staticmethod
    def from_item(item: Dict[str, Any]) -> User:
        """Convert item to User with version handling."""
        schema_version = item.get('schema_version', 1)
        
        if schema_version == 1:
            # Legacy format
            return User(
                id=item['user_id'],
                email=item['email'],
                name=item['name'],
                preferences=UserPreferences()  # Default preferences
            )
        elif schema_version == 2:
            # Current format
            return User(
                id=item['user_id'],
                email=item['email'],
                name=item['name'],
                preferences=UserPreferences(**item['preferences'])
            )
        else:
            raise ValueError(f"Unsupported schema version: {schema_version}")
```

**Rules:**

* Include schema_version in items for migrations.
* Handle multiple schema versions in mappers.
* Use scan operations carefully for large migrations.
* Test migrations thoroughly before production.


## 7. Query Optimization

### Efficient Query Patterns

```python
class OptimizedQueries:
    """Optimized DynamoDB query patterns."""
    
    async def get_user_activity_summary(self, user_id: str, 
                                      days: int = 30) -> Dict[str, Any]:
        """Get user activity efficiently."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Single query for multiple entity types
        response = await self.table.query(
            KeyConditionExpression=Key('pk').eq(f'user#{user_id}'),
            FilterExpression=Attr('created_at').gte(cutoff_date.isoformat()),
            ProjectionExpression='sk, entity_type, created_at, amount'
        )
        
        # Process results by entity type
        orders = []
        activities = []
        
        for item in response['Items']:
            if item['sk'].startswith('order#'):
                orders.append(item)
            elif item['sk'].startswith('activity#'):
                activities.append(item)
        
        return {
            'orders_count': len(orders),
            'total_spent': sum(float(order.get('amount', 0)) for order in orders),
            'activities_count': len(activities)
        }
    
    async def batch_get_users(self, user_ids: List[str]) -> List[User]:
        """Efficiently get multiple users."""
        if not user_ids:
            return []
        
        # Use batch_get_item for multiple items
        keys = [{'pk': f'user#{uid}', 'sk': 'profile'} for uid in user_ids]
        
        response = await self.dynamodb.batch_get_item(
            RequestItems={
                self.table_name: {
                    'Keys': keys,
                    'ProjectionExpression': 'pk, sk, user_id, email, name'
                }
            }
        )
        
        items = response['Responses'][self.table_name]
        return [UserMapper.from_item(item) for item in items]
```

**Rules:**

* Use ProjectionExpression to limit returned data.
* Batch operations for multiple items.
* Filter at query level when possible.
* Design keys to minimize scan operations.


## 8. Cost Optimization

### Efficient Storage Patterns

```python
# Minimize item size and storage costs
class CostOptimizedStorage:
    """Cost optimization patterns."""
    
    @staticmethod
    def compress_user_item(user: User) -> Dict[str, Any]:
        """Create compact user item."""
        return {
            'pk': f'u#{user.id}',          # Shorter keys
            'sk': 'p',                     # Abbreviated sort key
            't': 'user',                   # Short entity type
            'id': user.id,
            'e': user.email,               # Short attribute names
            'n': user.name,
            's': user.status,
            'c': user.created_at.isoformat(),
            'gsi1pk': f'e#{user.email}',
            'gsi1sk': f'u#{user.id}'
        }
    
    @staticmethod
    def use_sparse_gsi(item: Dict[str, Any]) -> Dict[str, Any]:
        """Only include GSI attributes when needed."""
        # Only add GSI attributes for active users
        if item.get('status') == 'active':
            item['gsi2pk'] = f"status#{item['status']}"
            item['gsi2sk'] = f"{item['created_at']}#{item['id']}"
        
        return item
```

**Rules:**

* Use shorter attribute names for frequently stored data.
* Implement sparse GSIs to reduce index costs.
* Archive or delete obsolete data regularly.
* Monitor and optimize frequently accessed patterns.


## 9. Quick Reference

### Key Design Patterns

```python
# Primary patterns
PK = 'entity_type#id'
SK = 'detail_type' or 'related_entity#id'

# GSI patterns  
GSI1PK = 'lookup_field#value'
GSI1SK = 'entity_type#id'

# Relationships
# One-to-many: Same PK, different SK
# Many-to-many: Use junction entities

# Optimistic locking
version: int                    # Version number
updated_at: datetime           # Timestamp check
```

### Common Commands

```python
# Repository operations
await repo.get_by_id(id)              # Get single item
await repo.query_by_pk(pk)            # Get related items  
await repo.gsi_query(index, gsi_pk)   # Alternative access
await repo.batch_get(ids)             # Multiple items
await repo.save_with_version(entity)  # Optimistic locking
```

**Rules:**

* Design for access patterns, not normalization.
* Use single table with proper key design.
* Implement GSIs for alternative queries.
* Use optimistic locking for data consistency.
* Optimize for cost and performance.