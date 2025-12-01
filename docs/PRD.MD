Product Requirements Document
(PRD)  

Sales Eco System
 
Jira Epic
[Link the epic link for reference - helpful to track engineering team’s progress] 
Delivery Date


Document Status
On Track
System Architecture


Product Manager
Asim Ibne Ilyus
Engineering Lead


Designer Lead


Quality Assurance (QA) Lead


Relevant Documents








1. Objective
To design a comprehensive digital ecosystem that enables SRs, ASMs, CROs, and BDOs to collaboratively manage retailer, partner and engineer onboarding, order creation, visits, stock and branding requests, retail point confirmations, potential site tagging, dispute resolution, and operational updates in a seamless, transparent, and automated manner.
2. Problem Statement
Current field sales processes are fragmented and lack a unified digital platform. Communication happens via calls and informal chats, making data tracking and accountability difficult. Multiple officers often duplicate work on the same lead due to the absence of a centralized visibility system.
 Approval processes for onboarding partners, retailers, and engineers are manual, slow, and error-prone. There’s no automated workflow for stock management, branding requests, or retail point confirmations. This leads to delays, missed opportunities, and a lack of operational efficiency.
3. Actors & Permissions
Actor
Responsibilities
SR
Retailer Registration, Order Creation, General Visit, Stock Management, Branding Request Form
ASM 
Retail Point Request Confirmation
CRO 
Partner Registration, General Visit, User Order Confirmation Visit, Uncovered Retailers Form, IHB Registration, Update Partner Form, Tag Potential Site Form
BDO 
Engineer Registration, General Visit, Potential Sites Registration, IHB Registration, Retail Point Request, Engineer Update Form
CRM
Retailer Registration, Order Creation, Partner Registration, User Order confirmation Visit, IHB Reg,Engineer Registration, Potential Sites Reg
Dispute Board
Dispute Resolution

4. Functional Requirements
4.1 General Visit 
Actors: SR, CRO, BDO
Purpose: Visit existing or potential retailers/partners/engineers for updates, monitoring, or issue resolution.
Notifications: Submission triggers notification to the respective reporting manager and the submitters.



4.2 SR Activities
4.2.1 Retailer Registration
Actor: SR, CRM 
Action: SR submits retailer details → CRM verifies. (On approval, retailers are activated in the system.)
Purpose: The purpose of Retailer Registration is to officially onboard and verify retailers in the system, enabling order processing, tracking, and eligibility for company programs.
Notifications: Submission triggers notification to the submitters and will get the notification after approved or rejected


4.2.2 Order Creation
Linked to a registered retailer or potential site.
Delivery Methods:


General Delivery: CRO visits and confirms before CRM approval.


Factory DN: Direct CRM approval.


Checkbox: "Eligible for Engineer/Partner Reward" → Notifies BDO & CRO.


4.2.3 Stock Management
SR updates stock availability at retailer location.


Fields: Retailer ID, Current Stock Levels, Notes.


4.2.4 Branding Request Form
Request for promotional material installation or branding activity at retailer site.


Approval via CRM.



4.3 ASM Functions
4.3.1 Retail Point Request Confirmation
ASM receives requests from BDO.


Confirms availability and feasibility before CRM updates.



4.4 CRO Functions
4.4.1 Partner Registration
CRO registers contractors/partners → CRM verifies.


Fields: Partner Name, Type, Contact, Experience, Docs.


4.4.2 User Order Confirmation Visit
CRO visits site for order verification (General Delivery).


Updates visit report before CRM approval.


4.4.3 Uncovered Retailers Form
CRO submits list of retailers in the area not yet covered.


Used for lead generation.


4.4.4 IHB Registration
Registers Individual House Builders (IHBs) → CRM verification.


4.4.5 Update Partner Form
Update partner details (contact changes, experience, etc.).


4.4.6 Tag Potential Site Form
CRO tags potential construction sites for follow-up.



4.5 BDO Functions
4.5.1 Engineer Registration
Registers engineers for projects → CRM verifies.


4.5.2 Potential Sites Registration
Logs new construction sites.


4.5.3 IHB Registration
Same as CRO’s IHB Registration.


4.5.4 Retail Point Request
Sends request to ASM for confirmation.


4.5.5 Engineer Update Form
Updates engineer data (projects, contact).



5. Process Flow (Redesigned from Reference Diagram)
Step 1 – Initiation
Any role starts their specific registration/update process.


Step 2 – Data Collection
Forms filled with necessary fields (auto validation for mandatory data).


Step 3 – Verification
CRM verifies submissions (approve/reject).


Approval triggers WhatsApp/in-app notifications to relevant roles.


Step 4 – Order Conversion
If order marked as General Delivery → CRO Visit → CRM Approval.


If Factory DN → Direct CRM Approval.


Step 5 – Reward & Disputes
Reward checkbox triggers notification to CRO & BDO.


Dispute Board handles disagreements.



6. Notifications
Trigger
Recipient
Retailer Registration
CRM
Partner/Engineer Onboarding
CRM
Order Created
CRO (if General Delivery), CRM
Reward Checkbox Selected
BDO, CRO
Dispute Raised
Dispute Board, CRM
Retail Point Request
ASM
Stock Update
ASM, CRM


7. Acceptance Criteria
All role-specific forms functional.


All workflows trigger correct notifications.


CRM can approve/reject with audit trail.


Orders correctly follow delivery path (General vs Factory DN).



8. Dependencies
CRM Verification Module


Notification Service (WhatsApp + In-App)


Dispute Management Module



9. KPIs
Time from registration to verification.


% of orders from General Delivery path.


Reward dispute resolution SLA.


Site-to-order conversion rate.



If you want, I can also redraw the process flow diagram in a cleaner, modern format to match this PRD so the roles, forms, and verification steps are visually clear like your reference image but updated for your new system. This will help in development handover.
Do you want me to make that new diagram next?



