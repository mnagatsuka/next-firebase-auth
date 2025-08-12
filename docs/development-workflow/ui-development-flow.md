# 📄 **UI Development Workflow**

This document outlines the standard UI development process, from planning to final implementation. The workflow is designed to be efficient, collaborative, and easy for both human developers and AI agents to follow.


## **1. Planning & Specification**

  * **Objective:** Define the new feature or page requirements.
  * **Action:** The team, led by a Product Manager and UX Designer, creates a **Page Specification (`.md`)** in the `/specs/ui/pages` directory.
  * **AI Instruction:** An AI agent will read this specification to understand the high-level goal, page layout, and required components. The spec acts as a blueprint for the final page.
  * **Key Deliverable:** A completed markdown file following the [Page Specification Template](https://www.google.com/search?q=%23) (e.g., `dashboard.md`).


## **2. Component Development**

  * **Objective:** Build and document individual, reusable UI components in isolation.
  * **Action:** A developer (or AI agent) identifies the necessary components from the page specification. Each component is built and documented with its various states and properties within **Storybook**.
  * **AI Instruction:**
    1.  Read the page specification to identify required components (e.g., `Button`, `UserCard`).
    2.  Check the existing Storybook library to see if a component already exists.
    3.  If a new component is needed, create its code and a corresponding `.stories.jsx/tsx` file. The story file must include clear definitions for all props and states.
  * **Key Deliverable:** A new component and its corresponding `.stories.jsx/tsx` file, accessible via the Storybook server.


## **3. Page Assembly**

  * **Objective:** Combine the documented components to build the final page layout and integrate it with the application's logic.
  * **Action:** Using the page specification as a guide, the developer assembles the components to create the final page file (e.g., `Dashboard.jsx/tsx`). This step involves writing the code that imports components, arranges them on the page, and connects them to data from the API.
  * **AI Instruction:**
    1.  Refer to the page specification for the page's structure and layout (e.g., "The `Header` component goes at the top, followed by a two-column grid with `AccountStatusCard` and `RecentActivity`").
    2.  Write the page-level code that imports the required components.
    3.  Implement the logic for user actions and data fetching as described in the specification's **Actions and Interactions** section.
  * **Key Deliverable:** A complete page file (e.g., `Dashboard.jsx/tsx`) that correctly renders the components and handles user interactions.


## **4. Review & Quality Assurance**

  * **Objective:** Verify that the completed UI meets all specifications and works as expected.
  * **Action:** The page is reviewed by designers and tested by the QA team. They use the original page specification and the Storybook component documentation as the source of truth for verification.
  * **AI Instruction:** An AI agent can perform automated checks to ensure the implemented UI matches the descriptions and data requirements in the page specification. It can also run visual regression tests against the Storybook stories to catch unexpected changes.
  * **Key Deliverable:** A fully functional and tested UI page that is ready for production.