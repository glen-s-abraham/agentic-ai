from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from .tools.query_runner_tool import QueryRunnerTool

query_runner_tool = QueryRunnerTool()


@CrewBase
class DBAnalyzer():
    """Debate crew"""


    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def schemalookup(self) -> Agent:
        return Agent(
            config=self.agents_config['schemalookup'],
            verbose=True,
            tools=[query_runner_tool]
        )

    @agent
    def pgquerygenerator(self) -> Agent:
        return Agent(
            config=self.agents_config['pgquerygenerator'],
            verbose=True,
            tools=[query_runner_tool]
        )
    
    @agent
    def data_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['data_analyst'],
            verbose=True
        )


    @task
    def pg_lookup(self) -> Task:
        return Task(
            config=self.tasks_config['pg_lookup'],
            verbose=True
        )
    
    @task
    def generatequery(self) -> Task:
        return Task(
            config=self.tasks_config['generatequery'],
            verbose=True
        )
    
    @task
    def analyzedata(self) -> Task:
        return Task(
            config=self.tasks_config['analyzedata'],
            verbose=True
        )

 
    @crew
    def crew(self) -> Crew:
        """Creates the Debate crew"""

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )
