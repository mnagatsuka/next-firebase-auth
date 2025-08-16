# Simple Blog Post App

This is a simple web application built with **Next.js** to demonstrate the core concepts of **Server-Side Rendering (SSR)** and **Client-Side Rendering (CSR)** in a single project. The app functions as a basic blog, allowing users to view a list of posts and read individual articles.

## Project Background

Developing a blog post app is an ideal way to learn Next.js because it provides clear use cases for both rendering methods. The public-facing content, which benefits from being fast and discoverable by search engines, can be pre-rendered on the server (SSR). The more dynamic, interactive parts of the application, like forms or comment sections, can be handled on the client (CSR), where interactivity and real-time updates are more important than initial page load speed or SEO.

## Core Features and Technology

### Next.js
- A React framework that enables both SSR and CSR, along with other powerful features like file-system routing.

### Server-Side Rendering (SSR)
- Used for the main pages of the application, specifically the blog post list and individual blog post pages.

### How it works
- When a user requests a page, Next.js fetches the data (e.g., a list of posts) on the server, renders the React components into static HTML, and sends the complete HTML page to the browser.

### Benefits
- Faster initial page loads for the user and improved SEO, as search engine crawlers can easily read the content.

### Client-Side Rendering (CSR)
- Used for interactive components where real-time updates are needed and SEO is not a concern.

### How it works
- The initial page load is a minimal HTML file, and the browser then fetches and renders the dynamic data (e.g., comments) using JavaScript after the page has loaded.

### Benefits
- A more interactive user experience without full page refreshes, and it reduces the server's workload.

## Application Structure

The app is broken down into the following key pages to showcase these rendering methods:

### Homepage (`/`)
- A list of all blog posts. This page uses **SSR**. The server fetches a list of post titles and summaries from an API and pre-renders the entire list.

### Individual Post Page (`/posts/[id]`)
- Displays the full content of a single blog post. This page also uses **SSR**. Based on the post's unique ID in the URL, the server fetches and renders the specific post's content.

### Comments Section
- Located on the individual post page, this component is a great example of **CSR**. It fetches and displays comments dynamically after the main post content has loaded. Users can add a new comment, and the comment list will update without a full page refresh.

### Post Creation/Editing Page (`/create-post`)
- An administrative page where a user can write or edit a blog post. This entire page uses **CSR**. It's a highly interactive form that handles state, validation, and API calls to save or update the data. Since this page is not for public viewing, SEO is not a factor.