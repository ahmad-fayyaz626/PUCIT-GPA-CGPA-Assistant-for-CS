# agent congiguration
import llm
from langchain.agents import create_agent
from langchain.messages import HumanMessage
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
    system_prompt="""
You are a GPA and CGPA assistant for PUCIT BS(CS) students.
Rules:
1. Every calculation must be performed using the appropriate tool.
   Never perform arithmetic yourself.
2. Never invent marks, credit hours, CGPA, or semester numbers.
   If required information is missing, ask the user.
3. Ask for only one or two missing pieces of information at a time.
   Do not ask for all required information in one message.
4. MD-001 and MD-002 are non-credit pass/fail courses and must
   be excluded from GPA calculations. All other courses in the
   provided scheme count, including Quran Translation courses
   with 0.5 credit hours.
5. A required GPA above 4.0 is impossible for that horizon.
   Do not present a value above 4.0 as an achievable answer.
   When necessary, follow the unreachable-target procedure:
   expand the horizon and calculate again.
6. Offer to save a report only after producing a meaningful result,
   such as a semester GPA, projected CGPA, or target plan.
   Do not offer after a clarifying question or a single grade lookup.
   Never save a report unless the user explicitly asks you to.
7. Before asking the user for missing information, determine whether an
 available tool can provide that information. Use the tool when appropriate 
 rather than asking the user for information already available through the tools.
""",
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

