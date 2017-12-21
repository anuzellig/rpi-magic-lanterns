module.exports = {
    apps : [
        {
            name: "sender",
            interpreter: "/usr/bin/python3",
            script: "./sender.py",
            watch: true,
            env: {
                "SNS_TOPIC": "arn:aws:sns:XXXXXXXXXXXX",
                "PROFILE": "magic-lanterns"
            }
        },
        {
            name: "listener",
            interpreter: "/usr/bin/python3",
            script: "./listener.py",
            watch: true,
            env: {
                "SQS_QUEUE_URL": "XXXXXXXXXXXX",
                "PROFILE": "magic-lanterns"
            }
        }
    ]
}