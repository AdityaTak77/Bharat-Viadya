from app.services.llm_interaction import get_llm, get_embeddings
from langchain.schema import SystemMessage
from langchain.agents.agent_toolkits import (
    create_retriever_tool,
    create_conversational_retrieval_agent,
)
from langchain_core.tools import BaseTool
from langchain_community.vectorstores import Milvus
from langchain.schema import Document


def aggregate_retrieved_texts(retrieved_documents: list[Document]) -> str:
    """
    Aggregate text from multiple retrieved documents.

    Args:
        retrieved_documents (list[Document]): List of retrieved documents.

    Returns:
        str: Aggregated text.
    """
    aggregated_text = " ".join([doc.page_content for doc in retrieved_documents])
    return aggregated_text


def get_context(user_message: str) -> str:
    """
    Fetch context from the Milvus vector database based on user input and generate
    a response using LangChain and OpenAI GPT models.

    Args:
        user_message (str): The user's input message.

    Returns:
        str: A string response from the conversational retrieval agent with
        Ayurvedic diagnostic information.
    """
    print(f"Original user message: {user_message}")
    llm = get_llm(temperature=0.1)
    embeddings = get_embeddings()

    vector_db = Milvus(
        embeddings,
        connection_args={"host": "localhost", "port": 19530},
        collection_name="ayurvedic_diagnosis",
    )

    # Ensure retrieval is specific and relevant
    health_diagnosis = vector_db.as_retriever(search_kwargs={"k": 10})  # Reduce k to focus on more specific documents

    health_tool = create_retriever_tool(
        health_diagnosis,
        "search-for-ayurvedic-diagnosis-context",
        "provides information about how to address health concerns using Ayurvedic principles",
    )

    tools: list[BaseTool] = [health_tool]

    system_message = SystemMessage(
        content='''
        You are a Virtual Ayurvedic Assistant, specialized in providing health diagnoses and remedies based on Ayurvedic principles. Your primary role is to deliver accurate Ayurvedic health information by leveraging the data stored in the Milvus database. 

        Guidelines for Interaction:

        1. Primary Source of Information: Strictly and always use the Milvus database as your first source for retrieving information related to the user's query. Your responses should strictly reflect the content found within this database.

        2. **Maintaining Query Integrity: When interpreting and responding to user queries, ensure that you do not alter the meaning or intent of the query. Use the exact wording and context provided by the user. Avoid substituting specific terms with broader or different ones unless explicitly instructed by the user.

        3. Response Format: Follow this strict format when responding to a user query:
           - WHAT IS THE DIAGNOSIS: Provide the diagnostic information as retrieved from the Milvus database.
           - HOW TO FIX IT: Give detailed treatment or remedy information based on the retrieved data.

        4. Herbs and Remedies:
            Always provide specific names of herbs or natural ingredients recommended for the treatment, along with comprehensive information about each herb, such as:
            
            Sanskrit and common names
            Primary uses
            Dosage and preparation methods
            Contraindications or precautions This ensures that users receive full details of how to effectively use Ayurvedic remedies.

        Remember, your effectiveness as an Ayurvedic Assistant depends on the accuracy, relevance, and reliability of the information you provide. Uphold these principles in all your interactions.
        '''
    )

    agent_executor = create_conversational_retrieval_agent(
        llm=llm,
        tools=tools,
        system_message=system_message,
        remember_intermediate_steps=True,
        verbose=True,
        max_token_limit=16000,
    )

    # Fetch relevant context from Milvus using the user's input
    retrieved_docs = health_diagnosis.get_relevant_documents(user_message)
    if not retrieved_docs:
        return "CURE NOT FOUND IN DATABASE"

    aggregated_context = aggregate_retrieved_texts(retrieved_docs)

    # Generate response using the aggregated context
    response = agent_executor(aggregated_context)
    response_text = response["output"]

    # Replace newline characters for better HTML rendering
    response_text = response_text.replace("HOW TO FIX IT", "<br /><br /> HOW TO FIX IT").replace("\n", "<br />")

    return response_text
