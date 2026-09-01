
# import os
# import shutil

# import streamlit as st
# import pandas as pd

# from matplotlib.figure import Figure

# from supervisor.graph import supervisor_graph

# from memory.conversation_memory import (
#     initialize_database,
#     create_thread,
#     get_threads,
#     get_thread,
#     update_thread_dataset,
#     update_thread_title,
#     save_message,
#     get_messages,
#     delete_thread
# )


# st.set_page_config(
#     page_title="Multi-Agent Assistant",
#     layout="wide"
# )


# initialize_database()


# if "active_thread_id" not in st.session_state:
#     st.session_state.active_thread_id = None


# def create_new_conversation():
#     thread_id = create_thread(
#         title="New Conversation"
#     )

#     st.session_state.active_thread_id = thread_id

#     st.rerun()


# st.title("DATA-MIND AI")


# with st.sidebar:

#     st.header(" Conversations")

#     if st.button(" New Conversation"):
#         create_new_conversation()


#     threads = get_threads()


#     if threads:

#         for thread in threads:

#             thread_id = thread[0]
#             title = thread[1]
#             dataset_name = thread[2]

#             label = title

#             if dataset_name:
#                 label += f" 📁 {dataset_name}"


#             if st.button(
#                 label,
#                 key=f"thread_{thread_id}"
#             ):
#                 st.session_state.active_thread_id = (
#                     thread_id
#                 )

#                 st.rerun()


#     st.divider()


# if st.session_state.active_thread_id is None:

#     thread_id = create_thread(
#         title="New Conversation"
#     )

#     st.session_state.active_thread_id = thread_id


# thread_id = (
#     st.session_state.active_thread_id
# )


# thread = get_thread(
#     thread_id
# )


# if thread is None:

#     thread_id = create_thread(
#         title="New Conversation"
#     )

#     st.session_state.active_thread_id = thread_id

#     thread = get_thread(
#         thread_id
#     )


# thread_title = thread[1]

# dataset_path = thread[2]

# dataset_name = thread[3]


# with st.sidebar:

#     st.header(" Dataset")

#     if dataset_name:

#         st.success(
#             f"Current dataset: {dataset_name}"
#         )

#     else:

#         st.info(
#             "No dataset uploaded for this conversation."
#         )


#     uploaded_file = st.file_uploader(
#         "Upload CSV",
#         type=["csv"],
#         key=f"upload_{thread_id}"
#     )


#     if uploaded_file is not None:

#         thread_upload_dir = os.path.join(
#             "data",
#             "uploads",
#             thread_id
#         )


#         os.makedirs(
#             thread_upload_dir,
#             exist_ok=True
#         )


#         upload_path = os.path.join(
#             thread_upload_dir,
#             uploaded_file.name
#         )


#         with open(
#             upload_path,
#             "wb"
#         ) as f:

#             f.write(
#                 uploaded_file.getbuffer()
#             )


#         update_thread_dataset(
#             thread_id,
#             upload_path,
#             uploaded_file.name
#         )


#         dataset_path = upload_path

#         dataset_name = uploaded_file.name


#         st.success(
#             f"Dataset saved to this conversation: {dataset_name}"
#         )


#         try:

#             preview_df = pd.read_csv(
#                 upload_path
#             )


#             st.dataframe(
#                 preview_df.head()
#             )


#         except Exception as e:

#             st.error(
#                 f"Could not read CSV: {e}"
#             )


#     if dataset_path and os.path.exists(dataset_path):

#         try:

#             preview_df = pd.read_csv(
#                 dataset_path
#             )

#             st.caption(
#                 f"Rows: {len(preview_df)}"
#             )

#             st.caption(
#                 f"Columns: {len(preview_df.columns)}"
#             )

#         except Exception:

#             pass


# st.subheader(
#     thread_title
# )


# messages = get_messages(
#     thread_id
# )


# for role, content, created_at in messages:

#     with st.chat_message(role):

#         st.write(content)


# query = st.chat_input(
#     "Ask something about your dataset..."
# )


# if query:

#     save_message(
#         thread_id,
#         "user",
#         query
#     )


#     with st.chat_message("user"):

#         st.write(query)


#     messages = get_messages(
#         thread_id
#     )


#     recent_messages = messages[-6:]


#     history_lines = []


#     for role, content, created_at in recent_messages:

#         history_lines.append(
#             f"{role}: {content}"
#         )


#     history_text = "\n".join(
#         history_lines
#     )


#     if not dataset_path:

#         dataset_path = (
#             "data/sample.csv"
#         )


#     with st.chat_message("assistant"):

#         with st.spinner(
#             "Thinking..."
#         ):

#             result = supervisor_graph.invoke(

#                 {

#                     "query": query,

#                     "route": "",

#                     "result": None,

#                     "csv_path": dataset_path,

#                     "history": history_text,

#                 }

#             )


#         answer = result["result"]

#         route = result["route"]


#         if isinstance(
#             answer,
#             Figure
#         ):

#             st.pyplot(answer)

#             stored_answer = (
#                 f"[Generated {route} visualization]"
#             )

#         else:

#             st.write(answer)

#             stored_answer = str(answer)


#         st.caption(
#             f"Routed to: {route}"
#         )


#     save_message(

#         thread_id,

#         "assistant",

#         stored_answer

#     )


#     existing_messages = get_messages(
#         thread_id
#     )


#     if len(existing_messages) == 2:

#         new_title = (
#             query[:40]
#             .strip()
#         )

#         if len(query) > 40:

#             new_title += "..."


#         update_thread_title(
#             thread_id,
#             new_title
#         )
import os

import streamlit as st

import pandas as pd


from matplotlib.figure import Figure


from supervisor.graph import (
    supervisor_graph
)



from memory.conversation_memory import (

    initialize_database,

    create_thread,

    get_threads,

    get_thread,

    update_thread_dataset,

    update_thread_title,

    save_message,

    get_messages,

    delete_thread

)



from memory.long_term_memory import (

    initialize_long_term_memory,

    extract_and_save_memory,

    get_all_memories,

    get_memory

)



st.set_page_config(

    page_title="DATA-MIND AI",

    layout="wide"

)



initialize_database()

initialize_long_term_memory()



if "active_thread_id" not in st.session_state:

    st.session_state.active_thread_id = None



def create_new_conversation():

    thread_id = create_thread(

        title="New Conversation"

    )


    st.session_state.active_thread_id = (
        thread_id
    )


    st.rerun()




st.title(
    " DATA-MIND AI"
)


st.caption(
    "Multi-Agent Data Analysis Assistant"
)



with st.sidebar:


    st.header(
        " Conversations"
    )


    if st.button(

        "+ New Conversation",

        use_container_width=True

    ):

        create_new_conversation()


    threads = get_threads()


    if threads:


        for thread in threads:


            thread_id = thread[0]

            title = thread[1]

            dataset_name = thread[2]


            label = title


            if dataset_name:

                label += (
                    f"  {dataset_name}"
                )


            if st.button(

                label,

                key=(
                    f"thread_{thread_id}"
                ),

                use_container_width=True

            ):


                st.session_state.active_thread_id = (
                    thread_id
                )


                st.rerun()


    st.divider()




if (

    st.session_state.active_thread_id
    is None

):


    thread_id = create_thread(

        title="New Conversation"

    )


    st.session_state.active_thread_id = (
        thread_id
    )



thread_id = (

    st.session_state.active_thread_id

)


thread = get_thread(
    thread_id
)



if thread is None:


    thread_id = create_thread(

        title="New Conversation"

    )


    st.session_state.active_thread_id = (
        thread_id
    )


    thread = get_thread(
        thread_id
    )



thread_title = thread[1]

dataset_path = thread[2]

dataset_name = thread[3]


with st.sidebar:


    st.header(
        "📁 Dataset"
    )


    if dataset_name:


        st.success(

            f"Current dataset: {dataset_name}"

        )


    else:


        st.info(

            "No dataset uploaded for this conversation."

        )


    uploaded_file = st.file_uploader(

        "Upload CSV",

        type=["csv"],

        key=(
            f"upload_{thread_id}"
        )

    )



    if uploaded_file is not None:


        thread_upload_dir = os.path.join(

            "data",

            "uploads",

            thread_id

        )


        os.makedirs(

            thread_upload_dir,

            exist_ok=True

        )


        upload_path = os.path.join(

            thread_upload_dir,

            uploaded_file.name

        )


        with open(

            upload_path,

            "wb"

        ) as f:


            f.write(

                uploaded_file.getbuffer()

            )


        update_thread_dataset(

            thread_id,

            upload_path,

            uploaded_file.name

        )


        dataset_path = upload_path

        dataset_name = uploaded_file.name


        st.success(

            f"Dataset saved: {dataset_name}"

        )



    if (

        dataset_path

        and

        os.path.exists(
            dataset_path
        )

    ):


        try:


            preview_df = pd.read_csv(

                dataset_path

            )


            st.caption(

                f"Rows: {len(preview_df)}"

            )


            st.caption(

                f"Columns: {len(preview_df.columns)}"

            )


            with st.expander(

                "Preview Dataset"

            ):


                st.dataframe(

                    preview_df.head()

                )


        except Exception as e:


            st.error(

                f"Could not read CSV: {e}"

            )




st.subheader(
    thread_title
)



messages = get_messages(
    thread_id
)


for role, content, created_at in messages:


    with st.chat_message(
        role
    ):


        st.write(
            content
        )



query = st.chat_input(

    "Ask something..."

)



if query:


    save_message(

        thread_id,

        "user",

        query

    )



    memory_result = (

        extract_and_save_memory(
            query
        )

    )



    with st.chat_message(
        "user"
    ):


        st.write(
            query
        )


    messages = get_messages(
        thread_id
    )


    recent_messages = messages[-8:]


    history_lines = []


    for role, content, created_at in recent_messages:


        history_lines.append(

            f"{role}: {content}"

        )


    history_text = "\n".join(

        history_lines

    )



    all_memories = get_all_memories()


    memory_lines = []


    for key, value, category in all_memories:


        memory_lines.append(

            f"{key}: {value}"

        )


    long_term_memory_text = "\n".join(

        memory_lines

    )



    if not dataset_path:


        dataset_path = (
            "data/sample.csv"
        )



    with st.chat_message(
        "assistant"
    ):


        with st.spinner(
            "Thinking..."
        ):


            result = supervisor_graph.invoke(

                {

                    "query": query,

                    "route": "",

                    "result": None,

                    "csv_path": dataset_path,

                    "history": history_text,

                    "long_term_memory": (
                        long_term_memory_text
                    ),

                }

            )


        answer = result[
            "result"
        ]


        route = result[
            "route"
        ]


       

        if isinstance(

            answer,

            Figure

        ):


            st.pyplot(
                answer
            )


            stored_answer = (

                f"[Generated {route} visualization]"

            )



        else:


            st.write(
                answer
            )


            stored_answer = str(
                answer
            )


        st.caption(

            f"Routed to: {route}"

        )


  

    save_message(

        thread_id,

        "assistant",

        stored_answer

    )



    existing_messages = get_messages(
        thread_id
    )


    if len(
        existing_messages
    ) == 2:


        new_title = (

            query[:40]

            .strip()

        )


        if len(
            query
        ) > 40:


            new_title += "..."


        update_thread_title(

            thread_id,

            new_title

        )