# agent congiguration
import llm
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from config.system_prompt import system_prompt
from tools import (
    save_report,
    marks_to_grade_points,
    calculate_new_cgpa,
    required_gpa_for_target,
    get_semester_courses,
    get_remaining_credit_hours,
    calculate_samester_gpa,
)

tools = [
    calculate_new_cgpa,
    required_gpa_for_target,
    get_semester_courses,
    get_remaining_credit_hours,
    calculate_samester_gpa,
    marks_to_grade_points,
    save_report,
]



agent = create_agent(
    model=llm.llm,
    tools=tools,
    system_prompt=system_prompt,
)

# messages = []
# while True:
#     user_input = input("User: ")
#     if user_input.lower() in ["exit", "quit"]:
#         break
#     messages.append(HumanMessage(content=user_input))
#     response = agent.invoke({"messages": messages})
#     print(response["messages"][-1].content)
#     messages = response["messages"]
# agent response
