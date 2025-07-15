#graph_main.py
from langgraph.graph import StateGraph
from nodes import create_agent_executor
from state_schema import MyStateSchema

graph_builder = StateGraph(state_schema=MyStateSchema)

graph_builder.add_node("agent_executor", create_agent_executor())
graph_builder.set_entry_point("agent_executor")
graph_builder.set_finish_point("agent_executor")

app = graph_builder.compile()

if __name__ == "__main__":
    print("🌍 Agent prêt, pose ta question (exit pour quitter)")
    while True:
        query = input("🧑 Toi : ")
        if query.lower() in ["exit", "quit", "q"]:
            print("👋 Bye")
            break
        result = app.invoke({"input": query})
        print(f"✅ Réponse : {result.get('output', 'Pas de réponse')}")
