[![recall_space_logo](logo.png)](https://recall.space/)

[![python](https://img.shields.io/badge/python-3.13-blue)](https://www.python.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

| Environment | Version |
| ----------- | ------- |
| Production  | 5.0.0   |
| Development | 5.0.0   |

+ `pip install "recall-space-agents[all]==4.0.2" --index-url "https://RecallSpace:<PAT>@pkgs.dev.azure.com/RecallSpace/recall-space-developments/_packaging/recall-space-agents/pypi/simple/"`
+ This will ask for user and password. Use your email and get a token from devops as password.
+ Use `pip install "recall-space-agent[postgresql]" ...` to enable `ChatDbToolKit`.
+ Use `pip install "recall-space-agent[microsoft_graph]" ...` to enable graph related toolkits.
+ Use `pip install"recall-space-agent[all]" ...` to install all.

# 🔅Introduction

The **Recall Space Agents** package leverages Langraph, Langchain, and 
the Agent Builder package to provide standard tools for agentic applications 
and high-level abstractions. This allows complex workflows to be expressed 
with just a few lines of code when the tasks are known and common.

If the workflows are not common or require special implementation, you can 
use Langraph and Langchain directly and then integrate them. The following 
are the main modules of this package:

+ **Hierarchical Applications:** In complex systems, it's often necessary to 
decompose tasks into smaller, manageable units. This hierarchical agents abstraction 
allows you to create a `Supervisor` that manages multiple `Worker` agents. 
The supervisor delegates tasks to workers and coordinates their execution to 
fulfill user requests. The system comprises three main components:
    + `Worker`: An abstract base class representing individual worker agents.
    + `Supervisor`: Manages workers and routes tasks to them. 
    + `ApplicationGraph`: Builds and manages the execution graph comprising 
    the supervisor and workers.

🅰️ The `Supervisor` has the ability to generate execution plans for complex tasks.
Internally, the `Supervisor` acts as a human proxy, commanding AI `Workers`.
Technically, this means that the `Supervisor` adds `Human` messages to the
conversation, while the `Workers` add `AI` messages. Only the `Supervisor`
knows about the overall plan and has access to the full context of the conversation.
The `Workers` receive a single command from the `Supervisor` each time and are
not aware of the conversation history.

✔️Please visit the example of [Open Purchase Orders](examples.md), to see Supervisor
with the plan flag activated.


:::mermaid
classDiagram
    class Worker {
        <<abstract>>
        +async get_worker_node(state: MessagesState) Command~Literal["supervisor"]~
        +agent_name: str
    }
    class Supervisor {
        -llm: AzureChatOpenAI
        -workers: dict~str, Worker~
        -system_prompt: str
        -require_plan : boolean
        +async supervisor_node(state: MessagesState) Command~str~
    }
    class ApplicationGraph {
        -supervisor: Supervisor
        -workers: dict~str, Worker~
        -graph: StateGraph
        +get_compiled_graph() StateGraph
        +async application_node(state: dict) dict
    }
    Worker <|-- EmailManager
    Worker <|-- TodoManager
    Worker <|-- SiteManager
    Worker <|-- SiteWorkbookManager
    Worker <|-- BotManager
    Supervisor "1" *-- "*" Worker : manages
    ApplicationGraph "1" *-- "1" Supervisor : uses
:::

+ **Realized Workers**: These are agents whose only tools are Recall Space Toolkits. 
This means their entire job is to fulfill tasks that are related to their attached toolkits.

+ **Toolkits**: These are functions with special metadata that allow LLMs to 
determine whether a function call is required to complete a task and what the 
parameters should be. `Toolkits` are collections of `Tools` organized based on the underlying client.

  As of today, 12-27-2024, the only underlying client is the Microsoft Graph API Python 
  SDK, organized by resource. For example, there is a `Toolkit` called `MSTodoToolKit`, 
  which contains `Tools` related to the Microsoft To Do app, connected via the 
  Microsoft Graph API. We plan to maintain this pattern as more `Toolkits` are 
  developed, continuing to build increasingly complex applications.

## Realized Workers
+ `EmailManager`
+ `TodoManager`
+ `SiteManager`
+ `SiteWorkbookManager`

## Toolkits
+ [MSEmailToolKit](recall_space_agents/toolkits/ms_email/README.md)
+ [MSTodoToolKit](recall_space_agents/toolkits/ms_todo/README.md)
+ [MSSiteToolKit](recall_space_agents/toolkits/ms_site/README.md)
+ [MSSiteWorkbookToolKit](recall_space_agents/toolkits/ms_site_workbook/README.md)
+ [MSBotToolKit](recall_space_agents/toolkits/ms_bot/README.md)
+ [MSGraphTokenToolKit](recall_space_agents/toolkits/ms_graph_token/README.md)


# 🚀Example: VIPUserApp.
+ *Example of a Complex Composed Double Hierarchical Applications*.

This hypothetical workflow represents a paid and free app for VIP users. 
Imagine that we, at Recall Space, have preferential access to Supplier Data, 
and that Lisa AI receives emails from general users inquiring about suppliers.

We are interested in some key users whom we have identified. These key users 
fall into two categories:

1. VIP Users Already Onboarded:
    + We want to provide them with daily updates about our best suppliers, 
    reinforcing our relationship and offering them exclusive value.
    + We want to create a TODO task to give special attention to their emails.
2. VIP Users Not Yet Onboarded but Who Have Emailed Us:
    + We aim to make them feel special by having Lisa AI reply with an 
    invitation to join, encouraging them to become onboarded users.

As a company with preferential access to suppliers, it is crucial for us to 
ensure that our VIP users receive timely and relevant information about our best 
suppliers. This strategy not only strengthens our relationships with these key 
clients but also leverages our unique position in the market.

Overall, the 'VIPUserApp' workflow enhances user engagement, promotes our unique 
offerings, and strengthens relationships with key clients—all while efficiently 
managing interactions based on each user's subscription status.

:::mermaid
graph TD
    Start[Start] --> CheckUserType{Is the user a paying user?}
    CheckUserType -- Yes --> PaidApplication[Invoke **Paid Application**]
    CheckUserType -- No --> FreeApplication[Invoke **Free Application**]

    FreeApplication --> CheckUnreadEmails1{Check if there are unread emails from user}
    CheckUnreadEmails1 -- Yes --> SendEmail1[Send an email to the user<br>Inviting them to join Recall Space<br>Your name is Lisa AI<br>Always be charming]
    CheckUnreadEmails1 -- No --> DoNothing1[Do nothing]
    SendEmail1 --> End
    DoNothing1 --> End

    PaidApplication --> CheckUnreadEmails2{Check if there are unread emails from user}
    CheckUnreadEmails2 -- Yes --> CreateTask[Create a TODO Task titled 'vip-emails'<br>Under TODO List 'daily routine' <br>Due in 2 hours<br> and Body: Summary of last unread email]
    CheckUnreadEmails2 -- No --> SendEmail2[Send an email to User A with a greeting and a summary of the content of the file Best Suppliers.xlsx.]
    CreateTask --> End
    SendEmail2 --> End

    End[End]
:::

    
## Define Free and Paid app.
```python
from azure.identity import UsernamePasswordCredential
from typing import Literal
from typing import TypedDict
from langgraph.types import Command
from recall_space_agents.hierarchical_agents.realized_workers.email_manager import EmailManager
from recall_space_agents.hierarchical_agents.realized_workers.todo_manager import TodoManager
from recall_space_agents.hierarchical_agents.realized_workers.site_manager import SiteManager
import os
from langchain_openai import AzureChatOpenAI
from langgraph.graph import END, START, StateGraph
from recall_space_agents.hierarchical_agents.supervisor import Supervisor
from recall_space_agents.hierarchical_agents.application_graph import ApplicationGraph

credentials = UsernamePasswordCredential(...)

llm = AzureChatOpenAI(...)

######
## Application 1
# workers
email_manager = EmailManager(llm=llm, credentials=credentials)
todo_manager = TodoManager(llm=llm, credentials=credentials)
site_manager = SiteManager(llm=llm, credentials=credentials)

workers = [email_manager, todo_manager, site_manager]

# supervisor
supervisor = Supervisor(llm=llm, workers=workers)

# Application 1
paid_application  = ApplicationGraph(supervisor)

######
## Application 2
# workers
workers = [email_manager]

# supervisor
supervisor = Supervisor(llm=llm, workers=workers)

# Application 2
free_application  = ApplicationGraph(supervisor)
```

+ link both Hierarchical applications with a custom logic defined in pure langraph.

```python
class VIPUserAppState(TypedDict):
    messages: list
    is_paying_user: bool
    user_email: str

def is_paid_user_node(state) -> Command[Literal["paid_application", "free_application"]]:
    next_node = "free_application"
    messages = [("user", 
        f"""
        Check if there are unread emails from '{state['user_email']}'
        if there are:
            - Send an email to that user, inviting him to join you at Recall Space.
            Your name is Lisa AI.
            Always be charming.
        else:
            - Do nothing.
        """)]
    if state["is_paying_user"] is True:
        next_node = "paid_application"
        messages = [("user",f"""
        Check if there are unread emails from '{state['user_email']}'.
        if there are:
            - Create a TODO Task titled 'vip-emails' under a TODO List called 'auto-app'.
            The task should be due for 2 hours from now, and the body should be the 
            summary of the last unread email received from the user.
        else:
            Send an email to the user with a greeting and a summary of 
            the content of the file '/General/Development/ERP System.xlsx'
            which you can get on the site 'Recall Space GmbH'. 

        Your name is Lisa AI.
        Note: The 'site_manager' worker can help you get the content of the file.
        Always be charming.
        """)]
    return Command(
                goto=next_node,
                update={"messages": messages},
            )

builder = StateGraph(VIPUserAppState)
builder.add_edge(START, "is_paid_user_node")
builder.add_node("is_paid_user_node", is_paid_user_node)
builder.add_node("paid_application", paid_application.application_node)
builder.add_node("free_application", free_application.application_node)
builder.add_edge("paid_application", END)
builder.add_edge("free_application", END)

# Demo app
demo_app = builder.compile()

response = await demo_app.ainvoke(
    {
    "messages": ["start you work"],
    "is_paying_user":True,
    "user_email": "gari.ciodaro@recall.space"
    }
)
```

:::mermaid
graph TD;
    __start__ --> is_paid_user_node;

    is_paid_user_node --> paid_app;
    is_paid_user_node --> free_app;

    paid_app --> __end__;
    free_app --> __end__;

    %% Paid App Subgraph
    subgraph Paid App
        paid_app --> supervisor_paid;
        supervisor_paid --> email_manager_paid;
        supervisor_paid --> todo_manager_paid;
        supervisor_paid --> site_manager_paid;
        email_manager_paid --> supervisor_paid;
        todo_manager_paid --> supervisor_paid;
        site_manager_paid --> supervisor_paid;
        supervisor_paid --> __end__;
    end

    %% Free App Subgraph
    subgraph Free App
        free_app --> supervisor_free;
        supervisor_free --> email_manager_free;
        email_manager_free --> supervisor_free;
        supervisor_free --> __end__;
    end
:::

# ❕ Key Notes on VIPUserApp

- **Logical Flow vs. Graph Structure**: The logical flow of the application differs from its graph representation.

- **Supervisor and Workers Abstraction**:
  - This abstraction is primarily used to enable Lisa AI to compose more complex applications with a reduced chance of failure.
  - It requires fewer tokens to generate, which naturally decreases the probability of errors or failures during generation.

- **Spectrum of Control in Workflow Design**:
  - You can exert varying levels of control over the workflow, but increased control often adds structural complexity.
    - **Using the Supervisor and Workers Abstraction**:
      - Simplifies the structural complexity of the workflow.
      - Introduces some uncertainty in execution due to higher-level abstraction.
    - **Using Raw Functions Under Node**:
      - Provides full control over the workflow.
      - Increases the structural complexity due to low-level configuration.


# More Examples:
+ [Open Purchase Orders](examples.md)
+ [SiteWorkbookManager](examples.md)

# Please review the WorkflowExecutionManagement
+ [workflow-execution-management](workflow-execution-management.md)

# Recall Space Agents

This repository contains the core agent framework and toolkits for Recall Space, including integrations with Microsoft Graph, Google APIs, Azure services, and more.

## Key Features
- Modular agent architecture for workflow automation
- Toolkits for Microsoft Graph, Azure, Google Calendar, and more
- Support for document processing, email, and data extraction
- Extensible with custom agents and toolkits

## Notable Toolkits
- **Microsoft Graph Token Toolkit**: Securely manage Microsoft Graph tokens using Azure Entra ID and Key Vault. See [`recall_space_agents/toolkits/ms_graph_token/README.md`](recall_space_agents/toolkits/ms_graph_token/README.md) for details.
- **Email Toolkit**: Automate email sending and retrieval via Microsoft Graph.
- **Google Calendar Toolkit**: Integrate with Google Calendar for scheduling and event management.
- **Azure Blob Toolkit**: Manage files and data in Azure Blob Storage.

## Installation
Install the package and its dependencies:

```bash
pip install -e .[all]
```

Or for Microsoft Graph support only:

```bash
pip install -e .[microsoft_graph]
```

## Development
- Python 3.13+
- See `setup.py` for optional dependencies

## License
Open source. See LICENSE for details.

## Usage Examples

### Token Management and Email Sending
Here's an example of how to use the MSGraphTokenToolkit to get access tokens and use them with other toolkits:

```python
from recall_space_agents.toolkits.ms_graph_token.ms_graph_token_toolkit import MsGraphTokenToolkit
from recall_space_agents.toolkits.ms_email.ms_email import MSEmailToolKit
from recall_space_agents.utils.raw_token_credential import RawTokenCredential

# Initialize MSGraphTokenToolkit
toolkit = MsGraphTokenToolkit(
    keyvault_url="https://your-keyvault.vault.azure.net/",
    client_id="your-client-id",
    tenant_id="your-tenant-id",
    client_secret="your-client-secret",
    redirect_uri="your-redirect-uri",
    scope=[
        "Mail.Read",
        "Mail.ReadWrite",
        "Mail.Send",
        "People.Read",
        "Contacts.Read",
        "Contacts.ReadWrite",
    ]
)

# Generate a consent link for a user
consent_link = await toolkit.agenerate_link_for_consent(email="user@example.com")

# Once user has given consent, generate an access token
access_token = await toolkit.agenerate_new_access_token(email="user@example.com")

# Use the access token with MSEmailToolKit
email_toolkit = MSEmailToolKit(credentials=RawTokenCredential(access_token))

# Send an email
response = await email_toolkit.asend_email(
    subject="Test Email",
    body_html="<h1>Hello World</h1>",
    to_recipient="recipient@example.com"
)

# Read unread emails
emails = await email_toolkit.aget_emails(
    limit=2,
    skip=0,
    filter="isRead eq false"
)
```

### Using with Agent-Based Architecture
For more complex workflows, you can use the agent-based architecture:

```python
from recall_space_agents.hierarchical_agents.realized_workers.ms_graph_token_manager import MsGraphTokenManager
from recall_space_agents.hierarchical_agents.application_graph import ApplicationGraph
from recall_space_agents.hierarchical_agents.supervisor import Supervisor

# Initialize token manager with LLM
token_manager = MsGraphTokenManager(
    llm=your_llm,
    keyvault_url="your-keyvault-url",
    client_id="your-client-id",
    tenant_id="your-tenant-id",
    client_secret="your-client-secret",
    redirect_uri="your-redirect-uri",
    scope=["Mail.Send", "Contacts.ReadWrite"]
)

# Set up supervisor with workers
workers = [token_manager]
supervisor = Supervisor(llm=your_llm, workers=workers)

# Create application graph
app = ApplicationGraph(supervisor).get_compiled_graph()

# Run the application
state = {
    "messages": [("user",
    """
    Please check if the user with email user@example.com has consented to Mail.Send scope,
    if no, please give me the consent link to send the consent request.
    """)]
}

async for response in app.astream(state, stream_mode="updates"):
    print(str(response))
```

## Toolkits
+ [MSEmailToolKit](recall_space_agents/toolkits/ms_email/README.md)
+ [MSTodoToolKit](recall_space_agents/toolkits/ms_todo/README.md)
+ [MSSiteToolKit](recall_space_agents/toolkits/ms_site/README.md)
+ [MSSiteWorkbookToolKit](recall_space_agents/toolkits/ms_site_workbook/README.md)
+ [MSBotToolKit](recall_space_agents/toolkits/ms_bot/README.md)
+ [MSGraphTokenToolKit](recall_space_agents/toolkits/ms_graph_token/README.md)