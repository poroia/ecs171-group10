# setup
FROM python:3.8
EXPOSE 8501
WORKDIR /
COPY requirements.txt ./requirements.txt
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt
COPY . .

# overriden by docker-compose
CMD streamlit run ./src/app.py

# streamlit specific
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
RUN mkdir -p .streamlit
RUN bash -c 'echo -e "\
[general]\n\
email = \"\"\n\
" > .streamlit/credentials.toml'
RUN bash -c 'echo -e "\
[server]\n\
enableXsrfProtection = false\n\
enableCORS = false\n\
" > .streamlit/config.toml'
