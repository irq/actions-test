FROM alpine:3.9

LABEL "com.github.actions.name"="Dump event"
LABEL "com.github.actions.description"="This action will dump the event triggering the action to the logs."
LABEL "com.github.actions.icon"="corner-right-down"
LABEL "com.github.actions.color"="blue"

ENTRYPOINT [ "sh", "-c", "cat /github/workflow/event.json" ]
