FROM python:3.13.1

WORKDIR /usr/src/freelance-assistant

EXPOSE 8443

COPY . /usr/src/freelance-assistant

RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium && playwright install-deps

CMD [ "python3", "bot.py" ]