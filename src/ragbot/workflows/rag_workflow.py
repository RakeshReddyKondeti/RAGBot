from typing import List

from llama_index.core import load_indices_from_storage
from llama_index.core.prompts import PromptTemplate
from llama_index.core.base.llms.types import ChatMessage, MessageRole
from llama_index.core.response_synthesizers import get_response_synthesizer
from llama_index.core.settings import Settings
from llama_index.core.schema import NodeWithScore
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.workflow import (
    Workflow,
    StartEvent,
    StopEvent,
    Event,
    step,
)


from ragbot.prompts import (
    DIABETES_FAQ_RAG_SYSTEM_PROMPT,
    NO_FAQ_RESULT_SYSTEM_PROMPT
)
from ragbot.storage import build_storage_context

class RetrievedResultsEvent(Event):
    question: str
    results: List[NodeWithScore]

class PostProcessedResultsEvent(Event):
    question: str
    results: List[NodeWithScore]

class NoResultsRetrievedEvent(Event):
    question: str


class RAGWorkflow(Workflow):
    def __init__(self,timeout = 120, verbose = True,):
        super().__init__(timeout=timeout, verbose=verbose)
   
        index = load_indices_from_storage(
            storage_context=build_storage_context(),
        )[0]

        self.prompt = PromptTemplate(
            template=DIABETES_FAQ_RAG_SYSTEM_PROMPT)
        self.no_faq_prompt = PromptTemplate(
            template=NO_FAQ_RESULT_SYSTEM_PROMPT)
        self.retriever = index.as_retriever(
            similarity_top_k=5,)
        self.postprocessor = SimilarityPostprocessor(
            similarity_cutoff= 0.85
        )

    @step
    async def start(self, ev: StartEvent) -> RetrievedResultsEvent | NoResultsRetrievedEvent:
        results = await self.retriever.aretrieve(ev.question)
        if not results:
            return NoResultsRetrievedEvent(question=ev.question)
        return RetrievedResultsEvent(results= results, question=ev.question)
    
    @step
    async def post_process(
        self, 
        ev: RetrievedResultsEvent
    ) -> PostProcessedResultsEvent | NoResultsRetrievedEvent:
        # Here you can add any post-processing logic
        # For now, we just return the results as is
        results = self.postprocessor.postprocess_nodes(ev.results)
        if not results:
            return NoResultsRetrievedEvent(question=ev.question)
        return PostProcessedResultsEvent(results=results, question=ev.question)
    
    @step
    async def handle_no_retrieved_results(
        self, 
        ev: NoResultsRetrievedEvent
    ) -> StopEvent:
        # Handle the case where no results were retrieved
        # For now, we just return an empty response

        print(self.no_faq_prompt)
        messages = [
            ChatMessage(
                role=MessageRole.SYSTEM,
                content=self.no_faq_prompt.template
            ),
            ChatMessage(
                role=MessageRole.USER,
                content=ev.question,
            ),
        ]

        for message in messages:
            print(f"{message.role}: {message.content}")
            print()

        gen = await Settings.llm.astream_chat(
            messages=messages,
        )

        return StopEvent((gen, []))
    
    @step
    async def stop(self, ev: PostProcessedResultsEvent) -> StopEvent:
        # This is where you would handle the final output
        # For now, we just return the results

        print(f"Type of results: {type(ev.results)}")
        print(f"Type of results[0]: {type(ev.results[0])}")
        print(f"Type of NodeWithScore: {type(ev.results[0].node)}")
        context_str = [
            f"Q{idx+1}. {result.text}\n A{idx+1}. {result.metadata.get("answer")}" 
            for (idx, result) in enumerate(ev.results)
        ]
        context_str = "\n\n".join(context_str)
        print(f"Context String: {context_str}")

        messages = [
            ChatMessage(
                role= MessageRole.SYSTEM,
                content= self.prompt.format(
                    context_str = context_str,
                )
            ),
            ChatMessage(
                role= MessageRole.USER,
                content= ev.question,
            ),
        ]

        for message in messages:
            print(f"{message.role}: {message.content}")
            print()

        gen = await Settings.llm.astream_chat(
            messages= messages,
        )

        
        return StopEvent((gen, ev.results))

