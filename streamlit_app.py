import streamlit as st
from openai import AuthenticationError


st.set_page_config(
    page_title="Agentic pattern studio",
    page_icon=":material/hub:",
    layout="wide",
)

SUGGESTIONS = [
    "What is the square of the average of 10 and 5?",
    "Define artificial intelligence.",
    "Why is the sky blue?",
]


@st.cache_resource(show_spinner=False)
def get_tool_using_workflow():
    from patterns.pattern_executer.tool_using.graph import build_graph

    return build_graph()


@st.cache_resource(show_spinner=False)
def get_planner_executor_workflow():
    from patterns.planner_executer.graph import build_graph

    return build_graph()


@st.cache_resource(show_spinner=False)
def get_supervisor_worker_workflow():
    from patterns.supervizer_worker.graph import build_graph

    return build_graph()


@st.cache_resource(show_spinner=False)
def get_reflection_workflow():
    from patterns.reflection.graph import build_graph

    return build_graph()


def queue_suggestion():
    selected = st.session_state.suggestion
    if selected:
        st.session_state.pending_prompt = selected
        st.session_state.suggestion = None


st.title("Agentic pattern studio", icon=":material/hub:")
st.caption("A practical workspace for exploring four agent workflows.")

pattern = st.segmented_control(
    "Pattern",
    options=[
        "Tool-using",
        "Planner-executor",
        "Supervisor-worker",
        "Reflection",
    ],
    default="Tool-using",
    key="pattern_mode",
)

st.session_state.setdefault("messages", [])
st.session_state.setdefault("planner_result", None)
st.session_state.setdefault("supervisor_result", None)
st.session_state.setdefault("reflection_result", None)

with st.sidebar:
    st.subheader("Workflow")
    if pattern == "Tool-using":
        st.badge("Arithmetic", icon=":material/calculate:", color="blue")
        st.badge("General answers", icon=":material/chat:", color="green")
        if st.button("New conversation", icon=":material/add:", width="stretch"):
            st.session_state.messages = []
            st.rerun()
    elif pattern == "Planner-executor":
        st.badge("Planner", icon=":material/format_list_numbered:", color="blue")
        st.badge("Executor", icon=":material/play_arrow:", color="green")
        if st.button("Clear result", icon=":material/delete:", width="stretch"):
            st.session_state.planner_result = None
            st.rerun()
    else:
        if pattern == "Supervisor-worker":
            st.badge("Supervisor", icon=":material/account_tree:", color="blue")
            st.badge("Math and leave workers", icon=":material/groups:", color="green")
            if st.button("Clear result", icon=":material/delete:", width="stretch"):
                st.session_state.supervisor_result = None
                st.rerun()
        else:
            st.badge("Generator", icon=":material/edit_note:", color="blue")
            st.badge("Critic", icon=":material/rate_review:", color="green")
            if st.button("Clear result", icon=":material/delete:", width="stretch"):
                st.session_state.reflection_result = None
                st.rerun()

if pattern == "Tool-using":
    st.subheader("Ask a question")
    if not st.session_state.messages:
        st.markdown("#### Start with a question")
        st.pills(
            "Try a question",
            options=SUGGESTIONS,
            label_visibility="collapsed",
            key="suggestion",
            on_change=queue_suggestion,
        )

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("intent") == "math":
                st.badge("Calculator", icon=":material/calculate:", color="blue")
            elif message.get("intent") == "general":
                st.badge("General", icon=":material/chat:", color="green")

    prompt = st.chat_input("Ask a question")
    if st.session_state.get("pending_prompt"):
        prompt = st.session_state.pop("pending_prompt")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        answer = ""
        intent = None
        with st.chat_message("assistant"):
            with st.status(":shimmer[Routing your question]", type="compact") as status:
                try:
                    result = get_tool_using_workflow().invoke({"question": prompt})
                    answer = result["result"]
                    intent = result.get("intent")
                    status.update(label="Answer ready", state="complete")
                except AuthenticationError:
                    answer = (
                        "OpenAI rejected the configured API key. Check `OPENAI_API_KEY` "
                        "in `.env` or your process environment."
                    )
                    status.update(label="Authentication failed", state="error")
                except ValueError as error:
                    if "OPENAI_API_KEY not found" in str(error):
                        answer = "Set `OPENAI_API_KEY` in `.env` before asking a question."
                    else:
                        answer = "The workflow could not process that request. Please rephrase it."
                    status.update(label="Could not complete request", state="error")
                except Exception:
                    answer = "The workflow encountered an error. Check the app terminal for details."
                    status.update(label="Could not complete request", state="error")

            st.markdown(answer)
            if intent == "math":
                st.badge("Calculator", icon=":material/calculate:", color="blue")
            elif intent == "general":
                st.badge("General", icon=":material/chat:", color="green")

        assistant_message = {"role": "assistant", "content": answer}
        if intent:
            assistant_message["intent"] = intent
        st.session_state.messages.append(assistant_message)
elif pattern == "Planner-executor":
    st.subheader("Plan and execute a task")
    st.caption("The planner breaks your task into steps; the executor generates a result for each step.")

    with st.form("planner_executor_form", border=False):
        task = st.text_area(
            "Task",
            placeholder="For example: Create a launch plan for a study app.",
            height=120,
        )
        submitted = st.form_submit_button(
            "Plan and execute",
            icon=":material/play_arrow:",
            type="primary",
        )

    if submitted:
        if not task.strip():
            st.warning("Enter a task to plan and execute.")
        else:
            error_message = None
            with st.status(":shimmer[Planning and executing]", type="compact") as status:
                try:
                    result = get_planner_executor_workflow().invoke({"task": task.strip()})
                    st.session_state.planner_result = {
                        "task": task.strip(),
                        "plan": result.get("plan", []),
                        "output": result.get("output", ""),
                    }
                    status.update(label="Task complete", state="complete")
                except AuthenticationError:
                    error_message = (
                        "OpenAI rejected the configured API key. Check `OPENAI_API_KEY` "
                        "in `.env` or your process environment."
                    )
                    status.update(label="Authentication failed", state="error")
                except ValueError as error:
                    if "OPENAI_API_KEY not found" in str(error):
                        error_message = "Set `OPENAI_API_KEY` in `.env` before running this pattern."
                    else:
                        error_message = "The workflow could not process that task. Please rephrase it."
                    status.update(label="Could not complete task", state="error")
                except Exception:
                    error_message = "The workflow encountered an error. Check the app terminal for details."
                    status.update(label="Could not complete task", state="error")

            if error_message:
                st.error(error_message)

    if st.session_state.planner_result:
        result = st.session_state.planner_result
        st.markdown("#### Task")
        st.write(result["task"])

        plan_column, output_column = st.columns(2)
        with plan_column:
            with st.container(border=True):
                st.markdown("#### Plan")
                for index, step in enumerate(result["plan"], start=1):
                    cleaned_step = step.strip().removeprefix("-").strip()
                    if cleaned_step:
                        st.markdown(f"{index}. {cleaned_step}")
        with output_column:
            with st.container(border=True):
                st.markdown("#### Execution result")
                st.markdown(result["output"] or "No steps were executed.")
elif pattern == "Supervisor-worker":
    st.subheader("Route a request to a worker")
    st.caption("The supervisor sends calculations to the math worker and PTO requests to the leave-balance worker.")

    with st.form("supervisor_worker_form", border=False):
        query = st.text_area(
            "Request",
            placeholder="For example: What is 18% of 250? or What is Alice's leave balance?",
            height=120,
        )
        submitted = st.form_submit_button(
            "Route request",
            icon=":material/account_tree:",
            type="primary",
        )

    if submitted:
        if not query.strip():
            st.warning("Enter a request for the supervisor.")
        else:
            error_message = None
            with st.status(":shimmer[Supervisor routing request]", type="compact") as status:
                try:
                    result = get_supervisor_worker_workflow().invoke(
                        {"query": query.strip()}
                    )
                    st.session_state.supervisor_result = {
                        "query": query.strip(),
                        "worker": result.get("worker", ""),
                        "expression": result.get("expression", ""),
                        "employee_name": result.get("employee_name", ""),
                        "result": result.get("result", ""),
                    }
                    status.update(label="Request complete", state="complete")
                except AuthenticationError:
                    error_message = (
                        "OpenAI rejected the configured API key. Check `OPENAI_API_KEY` "
                        "in `.env` or your process environment."
                    )
                    status.update(label="Authentication failed", state="error")
                except ValueError as error:
                    if "OPENAI_API_KEY not found" in str(error):
                        error_message = "Set `OPENAI_API_KEY` in `.env` before running this pattern."
                    else:
                        error_message = "The supervisor could not process that request. Please rephrase it."
                    status.update(label="Could not complete request", state="error")
                except Exception:
                    error_message = "The workflow encountered an error. Check the app terminal for details."
                    status.update(label="Could not complete request", state="error")

            if error_message:
                st.error(error_message)

    if st.session_state.supervisor_result:
        result = st.session_state.supervisor_result
        st.markdown("#### Request")
        st.write(result["query"])

        worker_labels = {
            "math": "Math worker",
            "leave": "Leave-balance worker",
        }
        st.badge(
            worker_labels.get(result["worker"], "Worker"),
            icon=":material/account_tree:",
            color="blue",
        )

        if result["expression"]:
            st.caption("Expression sent to calculator")
            st.code(result["expression"], language="python")
        if result["employee_name"]:
            st.caption(f"Employee: {result['employee_name']}")

        st.markdown("#### Result")
        st.markdown(result["result"] or "The selected worker returned no result.")
else:
    st.subheader("Draft, review, refine")
    st.caption("Reflection cycle: generator, critic, revision.")

    with st.form("reflection_form", border=False):
        task = st.text_area(
            "Task",
            value=(
                "Explain why Python is a good language for beginners in exactly 2 sentences. "
                "Mention simple syntax, strong community support, and the availability of libraries. "
                "Do not use fluff or extra paragraphs."
            ),
            height=120,
        )
        submitted = st.form_submit_button(
            "Run reflection",
            icon=":material/refresh:",
            type="primary",
        )

    if submitted:
        if not task.strip():
            st.warning("Enter a task for the generator and critic.")
        else:
            error_message = None
            with st.status(":shimmer[Generating and reviewing]", type="compact") as status:
                try:
                    result = get_reflection_workflow().invoke(
                        {
                            "task": task.strip(),
                            "attempts": 0,
                            "needs_revision": True,
                            "status": "pending",
                        }
                    )
                    st.session_state.reflection_result = {
                        "task": task.strip(),
                        "answer": result.get("final_answer", result.get("draft", "")),
                        "feedback": result.get("feedback", ""),
                        "attempts": result.get("attempts", 0),
                        "status": result.get("status", "unknown"),
                    }
                    status.update(label="Review complete", state="complete")
                except AuthenticationError:
                    error_message = (
                        "OpenAI rejected the configured API key. Check `OPENAI_API_KEY` "
                        "in `.env` or your process environment."
                    )
                    status.update(label="Authentication failed", state="error")
                except ValueError as error:
                    if "OPENAI_API_KEY not found" in str(error):
                        error_message = "Set `OPENAI_API_KEY` in `.env` before running this pattern."
                    else:
                        error_message = "The reflection workflow could not process that task."
                    status.update(label="Could not complete review", state="error")
                except Exception:
                    error_message = "The workflow encountered an error. Check the app terminal for details."
                    status.update(label="Could not complete review", state="error")

            if error_message:
                st.error(error_message)

    if st.session_state.reflection_result:
        result = st.session_state.reflection_result
        st.write(result["task"])

        answer_column, review_column = st.columns([2, 1])
        with answer_column:
            with st.container(border=True):
                st.markdown("#### Final answer")
                st.markdown(result["answer"] or "No answer was produced.")
        with review_column:
            with st.container(border=True):
                st.markdown("#### Review")
                if result["status"] == "approved":
                    st.badge("Approved", icon=":material/check_circle:", color="green")
                else:
                    st.badge("Needs improvement", icon=":material/rate_review:", color="orange")
                st.metric("Draft attempts", result["attempts"])
                st.caption(result["feedback"] or "No critic feedback was returned.")