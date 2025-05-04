# main.py
import yaml
import argparse
from dotenv import load_dotenv
from app.agent import TravelPlannerAgent

def load_config(config_path: str):
    """Load configuration from a YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def main():
    """Main entry point."""
    load_dotenv()
    
    parser = argparse.ArgumentParser(description='NoDetours: Personalized Travel Planner Agent')
    parser.add_argument('--config', type=str, default='config/config.yaml', help='Path to config file')
    parser.add_argument('--cli', action='store_true', help='Run in CLI mode instead of web app')
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    if args.cli:
        # Run in CLI mode (same as before)
        # Initialize agent
        agent = TravelPlannerAgent(config)
        
        print("Welcome to NoDetours Travel Planner!")
        print("Tell me about your travel plans, and I'll help you create the perfect itinerary.")
        print("Type 'exit' to quit.\n")
        
        while True:
            user_input = input("You: ")
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("\nThank you for using NoDetours Travel Planner. Happy travels!")
                break
            
            # Process user input
            output = agent.process_input(user_input)
            
            # Display itinerary
            print("\n--- Your Travel Itinerary ---\n")
            print(output.get("itinerary", ""))
            
            # Display packing list
            print("\n--- Packing Recommendations ---\n")
            print(output.get("packing_list", ""))
            
            # Display budget estimate
            print("\n--- Budget Estimate ---\n")
            print(output.get("estimated_budget", ""))
            print("\n")
    else:
        # Run as web app
        import uvicorn
        host = config.get("app", {}).get("host", "127.0.0.1")
        port = config.get("app", {}).get("port", 8000)
        
        print(f"Starting NoDetours web app at http://{host}:{port}")
        uvicorn.run("api.app:app", host=host, port=port, reload=True)

if __name__ == "__main__":
    main()