from lexrchainer_client import ClientInterface, AgentBuilder, AgentWrapper
import os
from dotenv import load_dotenv
import traceback

def test_client_interface():
    # Load environment variables
    load_dotenv()
    
    # Initialize client
    client = ClientInterface()
    
    # Test getting current user
    try:
        current_user = client.get_current_user()
        print("Successfully connected to API!")
        print(f"Current user: {current_user}")
        return client, current_user
    except Exception as e:
        print(f"Error connecting to API: {e}")
        return None, None

def test_load_agent(agent_id: str):
    client = ClientInterface()
    agent = client.load_agent(agent_id)
    # send message to agent
    response = agent.send_message("How are you?", streaming=False)
    print(f"Agent response: {response}")

def test_agent_builder(agent_name: str):
    # Create a simple agent
    try:
        agent = (AgentBuilder(agent_name)
            .with_model("azure/gpt-4o")
            .with_system_prompt("You are a helpful assistant. Use the tools provided to answer the user's question.")
            .with_tool("SerpTool")
            .with_tool("scrape_url")
            .create_agent())
        
        # Test sending a message
        print(f"sending message to agent")
        response = agent.send_message("What is the weather in Tokyo?", streaming=False)
        print("\nAgent test successful!")
        print(f"Agent response: {response}")
        return agent, response
    except Exception as e:
        traceback.print_exc()
        print(f"Error testing agent: {e}")
        return None, None

def test_agent_conversation(agent: AgentWrapper):
    """Test a multi-turn conversation with the agent"""
    try:
        # First message
        response1 = agent.send_message("What is your name?")
        print(f"First response: {response1}")
        
        # Second message using context from first response
        response2 = agent.send_message(f"Based on your previous response, can you help me with a task?")
        print(f"Second response: {response2}")
        
        return response1, response2
    except Exception as e:
        print(f"Error in conversation test: {e}")
        return None, None

def test_agent_memory(agent: AgentWrapper, previous_responses: list[str]):
    """Test if agent maintains context from previous conversation"""
    try:
        # Reference previous conversation
        response = agent.send_message("Can you summarize our previous conversation?")
        print(f"Memory test response: {response}")
        return response
    except Exception as e:
        print(f"Error in memory test: {e}")
        return None

def test_agent_capabilities(agent: AgentWrapper):
    """Test various agent capabilities"""
    try:
        # Test code generation
        code_response = agent.send_message("Write a simple Python function to calculate factorial")
        print(f"Code generation response: {code_response}")
        
        # Test explanation
        explain_response = agent.send_message("Explain how a binary search works")
        print(f"Explanation response: {explain_response}")
        
        return code_response, explain_response
    except Exception as e:
        print(f"Error in capabilities test: {e}")
        return None, None

def test_agent_chain_operations(agent: AgentWrapper):
    """Test a chain of operations where each step depends on the previous one"""
    try:
        # Step 1: Generate a list of numbers
        list_response = agent.send_message("Generate a list of 5 random numbers between 1 and 100")
        print(f"List generation response: {list_response}")
        
        # Step 2: Sort the numbers (using context from previous response)
        sort_response = agent.send_message("Now sort those numbers in ascending order")
        print(f"Sorting response: {sort_response}")
        
        # Step 3: Calculate statistics (using the sorted list)
        stats_response = agent.send_message("Calculate the mean and median of these sorted numbers")
        print(f"Statistics response: {stats_response}")
        
        return list_response, sort_response, stats_response
    except Exception as e:
        print(f"Error in chain operations test: {e}")
        return None, None, None

def test_agent_code_chain(agent: AgentWrapper):
    """Test a chain of code-related operations"""
    try:
        # Step 1: Generate a class
        class_response = agent.send_message("Create a Python class called 'Person' with name and age attributes")
        print(f"Class generation response: {class_response}")
        
        # Step 2: Add methods to the class
        methods_response = agent.send_message("Add a method to calculate birth year based on current age")
        print(f"Methods addition response: {methods_response}")
        
        # Step 3: Create an instance and use it
        instance_response = agent.send_message("Create an instance of the Person class and demonstrate its usage")
        print(f"Instance creation response: {instance_response}")
        
        return class_response, methods_response, instance_response
    except Exception as e:
        print(f"Error in code chain test: {e}")
        return None, None, None

def test_agent_analysis_chain(agent: AgentWrapper):
    """Test a chain of analysis operations"""
    try:
        # Step 1: Generate a dataset
        data_response = agent.send_message("Generate a small dataset of 5 students with their test scores")
        print(f"Dataset generation response: {data_response}")
        
        # Step 2: Analyze the data
        analysis_response = agent.send_message("Analyze the test scores and identify the highest and lowest performers")
        print(f"Analysis response: {analysis_response}")
        
        # Step 3: Make recommendations
        recommendations_response = agent.send_message("Based on the analysis, provide recommendations for improving scores")
        print(f"Recommendations response: {recommendations_response}")
        
        return data_response, analysis_response, recommendations_response
    except Exception as e:
        print(f"Error in analysis chain test: {e}")
        return None, None, None

if __name__ == "__main__":
    print("Testing Client Interface...")
    client, current_user = test_client_interface()
    #agent, initial_response = test_agent_builder("Test Assistant 106")
    #test_load_agent(agent.agent_user_id)
    
    if client and current_user:
        print("\nTesting Agent Builder...")
        agent, initial_response = test_agent_builder("Test Assistant 112")
        
        if agent:
            print("\nTesting Agent Conversation...")
            conv_response1, conv_response2 = test_agent_conversation(agent)

            if conv_response1 and conv_response2:
                print("\nTesting Agent Memory...")
                memory_response = test_agent_memory(agent, [conv_response1, conv_response2])
                
                if memory_response:
                    print("\nTesting Agent Capabilities...")
                    test_agent_capabilities(agent)
                    
                    print("\nTesting Agent Chain Operations...")
                    test_agent_chain_operations(agent)
                    
                    print("\nTesting Agent Code Chain...")
                    test_agent_code_chain(agent)
                    
                    print("\nTesting Agent Analysis Chain...")
                    test_agent_analysis_chain(agent)