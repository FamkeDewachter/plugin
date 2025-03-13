import streamlit as st

# Sample data for files and comments
files = {
    "File1.docx": [
        {
            "user": "John Doe",
            "timestamp": "2023-10-05",
            "comment": "Great work!",
            "resolved": False,
        },
        {
            "user": "Jane Smith",
            "timestamp": "2023-10-06",
            "comment": "Thanks!",
            "resolved": True,
        },
    ],
    "File2.pdf": [
        {
            "user": "Alice",
            "timestamp": "2023-10-07",
            "comment": "Can you add more details?",
            "resolved": False,
        },
    ],
}

# Sidebar for file selection
st.sidebar.title("Google Drive Comment Tool")
selected_file = st.sidebar.selectbox(
    "Select a file or version", list(files.keys())
)

# Main content area
st.title(f"Comments for: {selected_file}")

# Display existing comments
st.subheader("Existing Comments")
for idx, comment in enumerate(files[selected_file]):
    col1, col2 = st.columns([4, 1])
    with col1:
        st.write(
            f"**{comment['user']}** ({comment['timestamp']}): {comment['comment']}"
        )
    with col2:
        if st.button(f"Resolve {idx + 1}", key=f"resolve_{idx}"):
            files[selected_file][idx]["resolved"] = True
            st.success(f"Comment {idx + 1} resolved!")

# Add new comment
st.subheader("Add a New Comment")
new_comment = st.text_area(
    "Your comment", placeholder="Type your comment here..."
)
if st.button("Submit Comment"):
    if new_comment.strip():
        files[selected_file].append(
            {
                "user": "Current User",  # Replace with actual user name
                "timestamp": "2023-10-10",  # Replace with actual timestamp
                "comment": new_comment,
                "resolved": False,
            }
        )
        st.success("Comment added successfully!")
    else:
        st.error("Please enter a comment before submitting.")

# Display resolved comments separately (optional)
resolved_comments = [c for c in files[selected_file] if c["resolved"]]
if resolved_comments:
    st.subheader("Resolved Comments")
    for comment in resolved_comments:
        st.write(
            f"~~{comment['user']} ({comment['timestamp']}): {comment['comment']}~~"
        )
