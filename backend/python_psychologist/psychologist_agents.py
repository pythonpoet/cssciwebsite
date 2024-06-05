import os
from crewai import Agent, Task, Crew, Process

os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1" 

#os.environ['OPENAI_MODEL_NAME'] = 'mistralai/mistral-7b-instruct:free'
os.environ['OPENAI_MODEL_NAME'] = 'mistralai/mixtral-8x22b:free'
from key import *


def psychologist_find_insights(chat):
    # TODO clean messages
    psychologist = Agent(
        role='psychologist',
        goal='Analyses the chat-history: {chat} and finds out what went wrong in communication and behaviour to each other ',
        verbose=True,
        memory=True,
        backstory=(
            "This psychologist specialises in group therapy."
            "Very empathetic and very knowlegeable of various behaviour theories aswell as sociology and psychology"
            "You are absolutely neutral and you areable to find concensus between the most ego-centric and stubborn individuals."
            "Additionally, you write in the most constructive way possible"
        ),
        allow_delegation=True
    )
    # Creating a crew with the researcher and writer agents to collaborate on the project
    find_insights = Crew(
        agents=[psychologist],
        tasks=[mediate_chat,],
        process=Process.sequential  # Tasks will be executed one after the other
    )

    # Execute crew
    insights = find_insights.kickoff(inputs={
        'chat': chat_messages
        })
    return insights



