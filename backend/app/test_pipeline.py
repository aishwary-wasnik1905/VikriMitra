from backend.app.analytics_pipeline import build_response
from backend.agent.groq_agent import GroqAgent


def main():
    agent = GroqAgent()

    agent_result = agent.process_query(
        "Show monthly revenue and order count for 2017"
    )

    final_response = build_response(agent_result)

    print("Final VikriMitra response:")
    print(final_response)


if __name__ == "__main__":
    main()