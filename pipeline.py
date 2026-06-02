from agents import build_reader_agent,build_search_agent,writer_chain,critic_chain,revision_chain
import re

def parse_score(feedback: str) -> float:
    # Parse Score: X/10 or Score: X.Y/10
    match = re.search(r'score:\s*([\d\.]+)', feedback, re.IGNORECASE)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            pass
    return 0.0

def run_research_pipeline(topic : str, threshold: float = 8.0, max_loops: int = 3):

    state = {}
    state['revision_count'] = 0

    #Step-1
    yield "Searching the web...", state
    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        'messages':[('user',f"Find recent, detailed and reliable information about: {topic}")]
    })

    state['search_result'] = search_result['messages'][-1].content

    #Step-2
    yield "Scraping relevant content...", state
    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
        'messages':[("user",
                     f"Based on the following search results about {topic}"
                     f"pick the most relevant URL and scrape it for deeper content.\n\n"
                     f"Search results:\n{state['search_result'][:800]}")]

    })

    state['scraped_content'] = reader_result['messages'][-1].content

    #Step-3
    yield "Drafting research report...", state
    research_combined = (
        f"Search results: \n{state['search_result']}\n\n"
        f"Detailed scraped content: \n{state['scraped_content']}"
    )

    state['report'] = writer_chain.invoke({
        'topic':topic,
        'research' : research_combined
    })

    #Step-4
    yield "Critiquing the report...", state
    state['feedback'] = critic_chain.invoke({
        'report': state['report']
    })

    score = parse_score(state['feedback'])
    loop_count = 0

    while score < threshold and loop_count < max_loops:
        loop_count += 1
        state['revision_count'] = loop_count
        yield f"Revising report (Pass {loop_count}/{max_loops})... Score was {score}/10", state
        
        state['report'] = revision_chain.invoke({
            'topic': topic,
            'research': research_combined,
            'previous_report': state['report'],
            'feedback': state['feedback']
        })
        
        yield f"Re-evaluating report (Pass {loop_count}/{max_loops})...", state
        state['feedback'] = critic_chain.invoke({
            'report': state['report']
        })
        score = parse_score(state['feedback'])

    yield "Complete", state

if __name__ == "__main__":
    topic = input("Enter research topic: ")
    for status, state in run_research_pipeline(topic):
        print(f"[{status}]")
    if "report" in state:
        print("\nFinal Report:\n", state['report'])
    if "feedback" in state:
        print("\nCritic Report:\n", state['feedback'])