FROM python:3.6-alpine

LABEL "com.github.actions.name"="Push invitaitons model"
LABEL "com.github.actions.description"="Push new model versions out to consumers and create trello cards for code review."
LABEL "com.github.actions.icon"="upload"
LABEL "com.github.actions.color"="green"

# WORKDIR will be set to /github/workspace
# https://developer.github.com/actions/creating-github-actions/creating-a-docker-container/#workdir

RUN apk add --no-cache git

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY action.py ./

RUN echo $PWD
RUN echo $GITHUB_WORKSPACE
RUN ls -a .
RUN ls -a $GITHUB_WORKSPACE

# We don't care about args, so just run the script
# https://developer.github.com/actions/creating-github-actions/creating-a-docker-container/#entrypoint
ENTRYPOINT ["./action.py"]
