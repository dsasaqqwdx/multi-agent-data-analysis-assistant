
import os
import shutil

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

    get_all_memories

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


def remove_conversation(thread_id):

    active_thread_id = st.session_state.get(
        "active_thread_id"
    )

    
    delete_thread(thread_id)

   
    upload_dir = os.path.join(
        "data",
        "uploads",
        thread_id
    )

    if os.path.exists(upload_dir):
        shutil.rmtree(
            upload_dir,
            ignore_errors=True
        )

   
    visualization_dir = os.path.join(
        "data",
        "visualizations",
        thread_id
    )

    if os.path.exists(visualization_dir):
        shutil.rmtree(
            visualization_dir,
            ignore_errors=True
        )

   
    if active_thread_id == thread_id:

        remaining_threads = get_threads()

        if remaining_threads:

            st.session_state.active_thread_id = (
                remaining_threads[0][0]
            )

        else:

            st.session_state.active_thread_id = None

    st.rerun()



def save_visualization(

    figure,

    thread_id

):

    visualization_directory = os.path.join(

        "data",

        "visualizations",

        thread_id

    )


    os.makedirs(

        visualization_directory,

        exist_ok=True

    )


    filename = (

        f"chart_{uuid4_string()}.png"

    )


    image_path = os.path.join(

        visualization_directory,

        filename

    )


    figure.savefig(

        image_path,

        bbox_inches="tight",

        dpi=150

    )


    return image_path



def uuid4_string():

    import uuid

    return str(

        uuid.uuid4()

    )



st.title(

    " DATA-MIND AI"

)


st.caption(

    "Multi-Agent Data Analysis Assistant"

)



with st.sidebar:

    st.header(" Conversations")

    if st.button(
        "+ New Conversation",
        width="stretch"
    ):
        create_new_conversation()

    threads = get_threads()

    if threads:

        for thread in threads:

            sidebar_thread_id = thread[0]

            title = thread[1]

            dataset_name = thread[2]

            label = title

            if dataset_name:

                label += " folder"

            col1, col2 = st.columns(
                [5, 1]
            )

            with col1:

                if st.button(
                    label,
                    key=f"thread_{sidebar_thread_id}",
                    width="stretch"
                ):

                    st.session_state.active_thread_id = (
                        sidebar_thread_id
                    )

                    st.rerun()

            with col2:

                if st.button(
                    "-",
                    key=f"delete_{sidebar_thread_id}",
                    help="Delete this conversation",
                    width="stretch"
                ):

                    remove_conversation(
                        sidebar_thread_id
                    )

    else:

        st.info(
            "No conversations yet."
        )

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

        " Dataset"

    )



    if dataset_name:


        st.success(

            f"Current dataset: {dataset_name}"

        )


    else:


        st.info(

            "No dataset uploaded."

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


        

        if not os.path.exists(

            upload_path

        ):


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


            st.rerun()


        else:


            dataset_path = upload_path

            dataset_name = uploaded_file.name



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

                f" Rows: {len(preview_df)}"

            )


            st.caption(

                f" Columns: {len(preview_df.columns)}"

            )


            st.write(

                "### Preview"

            )


            st.dataframe(

                preview_df.head(5),

                use_container_width=True,

                hide_index=True

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


for message in messages:


    role = message[0]

    content = message[1]

    content_type = message[2]

    created_at = message[3]


    with st.chat_message(

        role

    ):



        if content_type == "image":


            if os.path.exists(

                content

            ):


                st.image(

                    content,

                    use_container_width=True

                )


            else:


                st.warning(

                    "Visualization file is no longer available."

                )



        else:


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

        query,

        content_type="text"

    )



    try:


        extract_and_save_memory(

            query

        )


    except Exception as e:


        print(

            f"Memory extraction error: {e}"

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


    for message in recent_messages:


        role = message[0]

        content = message[1]

        content_type = message[2]


        if content_type == "text":


            history_lines.append(

                f"{role}: {content}"

            )


        else:


            history_lines.append(

                f"{role}: [Visualization generated]"

            )


    history_text = "\n".join(

        history_lines

    )



    all_memories = get_all_memories()


    memory_lines = []


    for memory in all_memories:


        key = memory[0]

        value = memory[1]

        category = memory[2]


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


            try:


                result = supervisor_graph.invoke(

                    {

                        "query": query,

                        "route": "",

                        "result": None,

                        "csv_path": dataset_path,

                        "history": history_text,

                        "long_term_memory": (

                            long_term_memory_text

                        )

                    }

                )


                answer = result.get(

                    "result",

                    "No response generated."

                )


                route = result.get(

                    "route",

                    "unknown"

                )


            except Exception as e:


                answer = (

                    f"Error while processing request: {str(e)}"

                )


                route = "error"



        if isinstance(

            answer,

            Figure

        ):


            st.pyplot(

                answer

            )


            image_path = save_visualization(

                answer,

                thread_id

            )


            

            save_message(

                thread_id,

                "assistant",

                image_path,

                content_type="image"

            )


           

            save_message(

                thread_id,

                "assistant",

                f"Generated a {route} visualization.",

                content_type="text"

            )



        else:


            st.write(

                answer

            )


            save_message(

                thread_id,

                "assistant",

                str(answer),

                content_type="text"

            )



        st.caption(

            f"Routed to: {route}"

        )


    existing_messages = get_messages(

        thread_id

    )


    user_messages = [

        message

        for message in existing_messages

        if message[0] == "user"

    ]


    if len(

        user_messages

    ) == 1:


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


    st.rerun()