// Ambient module shims to avoid TS resolution errors in editors/CI
// These packages are installed and bundled externally; this shim unblocks typechecking.

declare module '@aws-sdk/lib-dynamodb';
declare module '@aws-sdk/client-apigatewaymanagementapi';

