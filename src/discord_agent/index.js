require('dotenv').config()
const { Client, Intents } = require('discord.js');
const client = new Client({ intents: [Intents.FLAGS.GUILDS, Intents.FLAGS.GUILD_MESSAGES] });
const {spawn} = require('child_process');


client.on('ready', () => {
    console.log(`Logged in as ${client.user.tag}!`)
})

let userName;
let userRequest;
let channelID;

client.on('messageCreate', async message => {
    const messageContent = message.content;
    const splitMessage = messageContent.split(' ')
    userName = message.author.username;
    channelID = message.channelId;

    if (userName === "speckly") {
        return
    }

    if (splitMessage[0].toLowerCase() === '!speckly') {
        userRequest = messageContent.substring(messageContent.indexOf(' ') + 1);
        const nlp_agent_py = spawn('python', ['-m', 'nlp_agent_cli', userName, userRequest, channelID]);
        nlp_agent_py.stdout.on('data', (data) => {
            let result = JSON.parse(data.toString());
            console.log(result);
            if (!("answer" in result)) {
                console.log("Warning, no answer found!");
                return
            }
            message.reply(result["answer"]);
            console.log(`Request from ${userName} answered`);
        });
    }
})

client.login(process.env.DISCORD_BOT_TOKEN)
