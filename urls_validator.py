import streamlit as st
import pandas as pd
import re
import csv
from io import StringIO
import base64
import time
import datetime as dt

# Set page config
st.set_page_config(
    page_title="URL Validator",
    page_icon="🔗",
    layout="wide"
)

valid_url_patterns = {
    "walmart_review_crawlerAPI": [
        r"https:\/\/www\.walmart\.[a-z\.]+\/reviews\/product\/\d+\?page=\d+$",
        r"http:\/\/www\.walmart\.[a-z\.]+\/reviews\/product\/\d+\?page=\d+$",
        r"https:\/.walmart\.[a-z\.]+\/reviews\/product\/\d+\?page=\d+$",
        r"https:\/\/www\.walmart\.[a-z\.]+\/reviews\/product\/\d+$",
        r"https:\/\/www\.walmart\.[a-z\.]+\/reviews\/product\/\d+\?page=\d+&page=\d+",
        r"https:\/\/www\.walmart\.[a-z\.]+\/reviews\/product\/\d+\?page=\d+-\d+"
    ],
    "walmart_product_link_crawlerAPI": [
        r"https:\/\/www\.walmart\.[a-z\.]+\/search\?q=.+",
        r"https:\/\/www\.walmart\.[a-z\.]+\/browse\/.+\/\d+_\d+_\d+_\d+\?module_search=browse_shelf&facet=brand%3A.+"
    ],
    "flipkart_review_crawlerAPI": [
        r"https:\/\/www\.flipkart\.[a-z\.]+\/.+\/product-reviews\/.+\?pid=.+&sortOrder=MOST_RECENT&certifiedBuyer=(true|false)&aid=overall",
        r"https:\/\/www\.flipkart\.[a-z\.]+\/.+\/product-reviews\/.+\?pid=.+&lid=.+&aid=overall&certifiedBuyer=(true|false)?(&sortOrder=(MOST_RECENT|RELEVANCE))?"
    ],
    "amazon_review_crawlerAPI": [
        r"https:\/\/www\.amazon\.[a-z\.]+\/product-reviews\/.+\/ref=cm_cr_arp_d_viewopt_srt\?ie=UTF8&reviewerType=all_reviews&sortBy=.+",
        r"https:\/\/www\.amazon\.[a-z\.]+\/.+\/product-reviews\/.+\/ref=cm_cr_arp_d_viewopt_srt\?ie=UTF8&reviewerType=all_reviews&sortBy=.+",
        r"https:\/\/www\.amazon\.[a-z\.]+\/.+\/product-reviews\/.+\/ref=cm_cr_dp_d_show_all_btm\?ie=UTF8&reviewerType=all_reviews&sortBy=.+",
        r"https:\/\/www\.amazon\.[a-z\.]+\/.+\/product-reviews\/.+\/ref=cm_cr_dp_d_show_all_btm\?ie=UTF8&reviewerType=all_reviews",
        r"https:\/\/www\.amazon\.[a-z\.]+\/.+\/product-reviews\/.+\?ie=UTF8&reviewerType=all_reviews&sortBy=.+",
        r"https:\/\/www\.amazon\.[a-z\.]+\/.+\/product-reviews\/.+\/ref=cm_cr_dp_d_show_all_btm",
        r"https:\/\/www\.amazon\.[a-z\.]+\/.+\/product-reviews\/.+\?ie=UTF8&reviewerType=all_reviews",
        r"https:\/\/www\.amazon\.[a-z\.]+\/product-reviews\/[^\/]+\/ref=[^?]+\?ie=UTF8&reviewerType=all_reviews(&sortBy=[^&]+)?",
        r"https:\/\/www\.amazon\.[a-z\.]+\/product-reviews\/[^\/]+\?ie=UTF8&reviewerType=all_reviews(&sortBy=[^&]+)?",
        r"https:\/\/www\.amazon\.[a-z\.]+\/.+\/product-reviews\/[^\/]+\?sortBy=.+",
        r"https:\/\/www\.amazon\.[a-z\.]+\/product-reviews\/[^\/]+\?ref=[^&]+&reviewerType=all_reviews(&filterByStar=[^&]+)?(&sortBy=[^&]+)?",
        r"https:\/\/www\.amazon\.[a-z\.]+\/product-reviews\/[^\/]+\?reviewerType=all_reviews(&filterByStar=[^&]+)?(&sortBy=[^&]+)?"
    ]
}

def validate_urls(source, urls):
    """Validate URLs based on the selected source"""
    if source not in valid_url_patterns:
        raise ValueError(f"Invalid source '{source}'. Available sources are: {list(valid_url_patterns.keys())}")
    
    patterns = valid_url_patterns[source]
    valid_urls = [url for url in urls if any(re.match(pattern, url) for pattern in patterns)]
    invalid_urls = [url for url in urls if url not in valid_urls]
    return valid_urls, invalid_urls

def get_csv_download_link(df, filename):
    """Generate a download link for a CSV file"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download {filename}</a>'
    return href

def main():
    # Add custom CSS
    st.markdown("""
        <style>
        .main {
            padding: 2rem;
        }
        .stAlert {
            margin-top: 1rem;
        }
        .download-link {
            margin: 1rem 0;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.title("🔗 URL Validator")
    st.markdown("Upload a CSV file containing URLs and validate them against different source patterns.")
    
    # Sidebar
    st.sidebar.header("Instructions")
    st.sidebar.markdown("""
    1. Select a source type
    2. Upload a CSV file containing URLs
    3. The CSV must have a column named 'url'
    4. Click 'Validate URLs' to process
    """)
    
    # Source selection
    source = st.selectbox(
        "Select Source",
        options=list(valid_url_patterns.keys()),
        help="Choose the source type for URL validation"
    )
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload CSV file",
        type=["csv"],
        help="Upload a CSV file containing URLs to validate"
    )
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            
            if 'url' not in df.columns:
                st.error("The CSV file must contain a column named 'url'")
            else:
                if st.button("Validate URLs", type="primary"):
                    with st.spinner("Validating URLs..."):
                        # Validate URLs
                        valid_urls, invalid_urls = validate_urls(source, df['url'].values.tolist())
                        
                        # Create DataFrames
                        valid_df = pd.DataFrame(valid_urls, columns=['Valid URLs'])
                        invalid_df = pd.DataFrame(invalid_urls, columns=['Invalid URLs'])
                        
                        # Display results in tabs
                        tab1, tab2 = st.tabs(["Valid URLs", "Invalid URLs"])
                        
                        with tab1:
                            st.success(f"Found {len(valid_urls)} valid URLs")
                            if len(valid_urls) > 0:
                                st.dataframe(valid_df, use_container_width=True)
                                st.markdown(get_csv_download_link(valid_df, f"valid_urls_{dt.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"), unsafe_allow_html=True)
                        
                        with tab2:
                            if len(invalid_urls) > 0:
                                st.error(f"Found {len(invalid_urls)} invalid URLs")
                                st.dataframe(invalid_df, use_container_width=True)
                                st.markdown(get_csv_download_link(invalid_df, f"invalid_urls_{dt.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"), unsafe_allow_html=True)
                            else:
                                st.success("No invalid URLs found!")
                        
                        # Display summary
                        st.markdown("### Summary")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Valid URLs", len(valid_urls))
                        with col2:
                            st.metric("Invalid URLs", len(invalid_urls))
                            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.warning("Please make sure your CSV file is properly formatted and try again.")

if __name__ == "__main__":
    main()