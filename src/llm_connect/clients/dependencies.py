from fastapi import Depends, Request
from openai import AsyncOpenAI
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from llm_connect.repositories.ActivityRepository import ActivityRepository
from llm_connect.repositories.AtomicPointEmbeddingRepository import (
    AtomicPointEmbeddingRepository,
)
from llm_connect.repositories.AtomicPointRelationRepository import (
    AtomicPointRelationRepository,
)
from llm_connect.repositories.AtomicPointRepository import AtomicPointRepository
from llm_connect.repositories.AtomicPointTagRepository import AtomicPointTagRepository
from llm_connect.repositories.ConversationRepository import ConversationRepository
from llm_connect.repositories.InteractionRepository import InteractionRepository
from llm_connect.repositories.LearnerRepository import LearnerRepository
from llm_connect.repositories.MasteryRepository import MasteryRepository
from llm_connect.repositories.MessageRepository import MessageRepository
from llm_connect.repositories.SessionRepository import SessionRepository
from llm_connect.repositories.TagRepository import TagRepository
from llm_connect.services.ActivityService import ActivityService
from llm_connect.services.analyzer import Analyzer
from llm_connect.services.AtomicPointService import AtomicPointService
from llm_connect.services.AtomicPointEmbeddingService import (
    AtomicPointEmbeddingService,
)
from llm_connect.services.ChatService import ChatService
from llm_connect.services.ConversationService import ConversationService
from llm_connect.services.core.Adapter import Adapter
from llm_connect.services.core.aevaluator import AEvaluator
from llm_connect.services.core.BKTEngine import BKTEngine
from llm_connect.services.core.Bridge import Bridge
from llm_connect.services.core.Companion import (
    Brain,
    Companion,
    Knowledge,
    Memory,
    Persionality,
    Tool,
)
from llm_connect.services.core.Evaluator import Evaluator
from llm_connect.services.core.MasteryEngine import MasteryEngine
from llm_connect.services.core.RolePlaySessionManager import RolePlaySessionManager
from llm_connect.services.core.TaskManager import (
    FillTaskManager,
    GenerateTaskManager,
    MatchTaskManager,
    ReorderTaskManager,
    SelectTaskManager,
)
from llm_connect.services.immerse import Actor, Orchestrator, PromptBuilder
from llm_connect.services.LearnerService import LearnerService
from llm_connect.services.MasteryService import MasteryService
from llm_connect.services.MessageService import MessageService
from llm_connect.services.SessionService import SessionService
from llm_connect.services.TagService import TagService


# 🤷‍♂️ Outside clients, created in lifespan
def get_llm(request: Request) -> AsyncOpenAI:
    return request.app.state.llm


def get_postgre_pool(request: Request):
    return request.app.state.pool


def get_redis(request: Request):
    return request.app.state.redis


def get_http_client(request: Request):
    return request.app.state.http_client


def get_s3_session(request: Request):
    return request.app.state.s3_session


async def get_db_session(request: Request):
    async with request.app.state.session_maker() as session:
        yield session


# 😵‍💫 Controlled services/repositories
# router is linked to app already
def get_prompt_builder():
    return PromptBuilder()


# def get_evaluator(
#     client: AsyncOpenAI = Depends(get_llm),
#     prompt_builder: PromptBuilder = Depends(get_prompt_builder),
# ):
#     return Evaluator(client, prompt_builder)


def get_actor(
    client: AsyncOpenAI = Depends(get_llm),
    prompt_builder: PromptBuilder = Depends(get_prompt_builder),
):
    return Actor(client, prompt_builder)


def get_analyzer():
    return Analyzer()


def get_aevaluator():
    return AEvaluator()


def get_session_repo(
    session: AsyncSession = Depends(get_db_session),
):
    return SessionRepository(
        session=session,
    )


def get_BKTEngine():
    return BKTEngine()


def get_mastery_repo(
    session: AsyncSession = Depends(get_db_session),
):
    return MasteryRepository(session=session)


def get_ap_repo(
    session: AsyncSession = Depends(get_db_session),
):
    return AtomicPointRepository(
        session=session,
    )


def get_mastery_engine(
    engine: BKTEngine = Depends(get_BKTEngine),
    mastery_repo: MasteryRepository = Depends(get_mastery_repo),
    ap_repo: AtomicPointRepository = Depends(get_ap_repo),
    session: AsyncSession = Depends(get_db_session),
):
    return MasteryEngine(engine, mastery_repo, ap_repo=ap_repo, session=session)


def get_evaluator(
    ses_repo: SessionRepository = Depends(get_session_repo),
    m_e: MasteryEngine = Depends(get_mastery_engine),
):
    return Evaluator(
        ses_repo,
        m_e,
    )


def get_roleplay_session_manager(
    prompt_builder: PromptBuilder = Depends(get_prompt_builder),
    client: AsyncOpenAI = Depends(get_llm),
    session_repo: SessionRepository = Depends(get_session_repo),
    e: Evaluator = Depends(get_evaluator),
):
    return RolePlaySessionManager(
        prompt_builder,
        client,
        session_repo,
        e,
    )


def get_activity_repo():
    return ActivityRepository()


def get_learner_repository(session: AsyncSession = Depends(get_db_session)):
    return LearnerRepository(session)


def get_adapter(
    l_r=Depends(get_learner_repository),
    a_r=Depends(get_activity_repo),
    mastery_repo: MasteryRepository = Depends(get_mastery_repo),
    ap_repo: AtomicPointRepository = Depends(get_ap_repo),
):
    return Adapter(
        l_r=l_r,
        a_r=a_r,
        mastery_repo=mastery_repo,
        ap_repo=ap_repo,
    )


def get_generate_task_manager(
    promp_builder: PromptBuilder = Depends(get_prompt_builder),
    client: AsyncOpenAI = Depends(get_llm),
):
    return GenerateTaskManager(
        prompt_builder=promp_builder,
        client=client,
    )


def get_select_task_manager():
    return SelectTaskManager()


def get_fill_task_manager():
    return FillTaskManager()


def get_match_task_manager():
    return MatchTaskManager()


def get_reorder_task_manager():
    return ReorderTaskManager()


def get_interaction_repo(
    session: AsyncSession = Depends(get_db_session),
):
    return InteractionRepository(
        session=session,
    )


def get_orchestrator(
    evaluator: Evaluator = Depends(get_evaluator),
    actor: Actor = Depends(get_actor),
    prompt_builder: PromptBuilder = Depends(get_prompt_builder),
    analyzer: Analyzer = Depends(get_analyzer),
    aevaluator: AEvaluator = Depends(get_aevaluator),
    session_manager: RolePlaySessionManager = Depends(get_roleplay_session_manager),
    session_repo: SessionRepository = Depends(get_session_repo),
    activity_repo: ActivityRepository = Depends(get_activity_repo),
    l_repo: LearnerRepository = Depends(get_learner_repository),
    task_manager: GenerateTaskManager = Depends(get_generate_task_manager),
    mastery_engine: MasteryEngine = Depends(get_mastery_engine),
    session: AsyncSession = Depends(get_db_session),
    select_task_manager: SelectTaskManager = Depends(get_select_task_manager),
    fill_task_manager: FillTaskManager = Depends(get_fill_task_manager),
    match_task_manager: MatchTaskManager = Depends(get_match_task_manager),
    reorder_task_manager: ReorderTaskManager = Depends(get_reorder_task_manager),
    generate_task_manager: GenerateTaskManager = Depends(get_generate_task_manager),
    interaction_repo: InteractionRepository = Depends(get_interaction_repo),
):
    return Orchestrator(
        evaluator,
        actor,
        prompt_builder,
        analyzer,
        aevaluator,
        session_manager,
        session_repo,
        activity_repo,
        l_repo,
        task_manager,
        mastery_engine,
        session,
        select_task_manager,
        fill_task_manager,
        match_task_manager,
        reorder_task_manager,
        generate_task_manager,
        interaction_repo,
    )


def get_chat_service(
    llm: AsyncOpenAI = Depends(get_llm),
    redis: Redis = Depends(get_redis),
    orchestrator: Orchestrator = Depends(get_orchestrator),
):
    return ChatService(llm, redis, orchestrator)


def get_learner_service(
    learner_repository: LearnerRepository = Depends(get_learner_repository),
    a: Adapter = Depends(get_adapter),
):
    return LearnerService(
        learner_repository,
        a,
    )


def get_conversation_repo(
    session: AsyncSession = Depends(get_db_session),
):
    return ConversationRepository(session=session)


def get_session_service(
    orchestrator: Orchestrator = Depends(get_orchestrator),
    session_repo: SessionRepository = Depends(get_session_repo),
    activity_repo: ActivityRepository = Depends(get_activity_repo),
    con_repo: ConversationRepository = Depends(get_conversation_repo),
    session: AsyncSession = Depends(get_db_session),
):
    return SessionService(
        orchestrator,
        session_repo,
        activity_repo,
        con_repo,
        session=session,
    )


def get_activity_service(
    activity_repo: ActivityRepository = Depends(get_activity_repo),
    adapter: Adapter = Depends(get_adapter),
    learner_repo: LearnerRepository = Depends(get_learner_repository),
    ap_repo: AtomicPointRepository = Depends(get_ap_repo),
):
    return ActivityService(
        activity_repo,
        adapter=adapter,
        learner_repo=learner_repo,
        ap_repo=ap_repo,
    )


def get_message_repo(
    session: AsyncSession = Depends(get_db_session),
):
    return MessageRepository(
        session=session,
    )


def get_ap_embedding_repo(
    session: AsyncSession = Depends(get_db_session),
):
    return AtomicPointEmbeddingRepository(session)


def get_ap_embedding_service(
    llm: AsyncOpenAI = Depends(get_llm),
    repo: AtomicPointEmbeddingRepository = Depends(get_ap_embedding_repo),
):
    return AtomicPointEmbeddingService(llm=llm, repo=repo)


def get_companion(
    llm=Depends(get_llm),
    learner_repo=Depends(get_learner_repository),
    con_repo=Depends(get_conversation_repo),
    pb=Depends(get_prompt_builder),
    ses_repo=Depends(get_session_repo),
    ac_repo=Depends(get_activity_repo),
    ap_repo=Depends(get_ap_repo),
    message_repo=Depends(get_message_repo),
    mastery_repo=Depends(get_mastery_repo),
    interaction_repo=Depends(get_interaction_repo),
    embedding_service: AtomicPointEmbeddingService = Depends(get_ap_embedding_service),
):
    # Create the brain of the companion
    # Not dpendencies, but like
    # Parts of the companion
    brain = Brain(llm, pb=pb)

    memory = Memory(
        learner_repo,
        con_repo,
        ses_repo,
        ac_repo,
        message_repo=message_repo,
        mastery_repo=mastery_repo,
        ap_repo=ap_repo,
        interaction_repo=interaction_repo,
    )

    k = Knowledge(ap_repo)

    # FIXME: Not needed in prototype

    p = Persionality()

    bridge = Bridge()
    tool = Tool(bridge=bridge)

    return Companion(
        brain,
        memory,
        k,
        p,
        pb,
        tool,
        embedding_service,
    )


def get_conversation_service(
    con_repo=Depends(get_conversation_repo),
    com=Depends(get_companion),
    session: AsyncSession = Depends(get_db_session),
    message_repo: MessageRepository = Depends(get_message_repo),
):
    return ConversationService(
        con_repo,
        com,
        session=session,
        message_repo=message_repo,
    )


def get_tag_repo(
    session: AsyncSession = Depends(get_db_session),
):
    return TagRepository(ses=session)


def get_apt_repo(
    session: AsyncSession = Depends(get_db_session),
):
    return AtomicPointTagRepository(
        session=session,
    )


def get_ap_relation_repo(
    session: AsyncSession = Depends(get_db_session),
):
    return AtomicPointRelationRepository(session)


def get_ap_s(
    ap_repo: AtomicPointRepository = Depends(get_ap_repo),
    tag_repo: TagRepository = Depends(get_tag_repo),
    ap_tag_repo: AtomicPointTagRepository = Depends(get_apt_repo),
    session: AsyncSession = Depends(get_db_session),
    ap_relation_repo: AtomicPointRelationRepository = Depends(get_ap_relation_repo),
    embedding_service: AtomicPointEmbeddingService = Depends(get_ap_embedding_service),
):
    return AtomicPointService(
        ap_repo=ap_repo,
        tag_repo=tag_repo,
        ap_tag_repo=ap_tag_repo,
        session=session,
        ap_relation_repo=ap_relation_repo,
        embedding_service=embedding_service,
    )


def get_mastery_service(
    m_repo: MasteryRepository = Depends(get_mastery_repo),
):
    return MasteryService(m_repo)


def get_tag_ser(
    repo: TagRepository = Depends(get_tag_repo),
    session: AsyncSession = Depends(get_db_session),
):
    return TagService(session=session, repo=repo)


def get_message_service(
    repo: MessageRepository = Depends(get_message_repo),
    session: AsyncSession = Depends(get_db_session),
):
    return MessageService(
        repo=repo,
        session=session,
    )
