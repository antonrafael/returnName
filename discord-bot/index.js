require('dotenv').config()
const { Client, Intents } = require('discord.js');
const client = new Client({ intents: [Intents.FLAGS.GUILDS, Intents.FLAGS.GUILD_MESSAGES] });
const express = require('express');
const {spawn} = require('child_process');
const axios = require('axios');

const app = express();
const port = 3000;

client.on('ready', () => {
    console.log(`Logged in as ${client.user.tag}!`)
})

client.on('messageCreate', async message => {
    const messageContent = message.content;
    const splitMessage = messageContent.split(' ')

    if (splitMessage[0] === '!speckly') {
        const userName = message.author.username;
        // const channel = message.channelId;
        const userRequest = messageContent.substring(messageContent.indexOf(' ') + 1);

        let result;
        app.get('/', (req, res) => {

            const nlp_agent_py = spawn('python', ['-m', 'nlp_agent_cli.py', userName, userRequest]);
            nlp_agent_py.stdout.on('data', function (data) {
                result = data.toString();
            });
            nlp_agent_py.on('close', (code) => {
                console.log(`Process closed stdio with code ${code}`); // send data to browser
                res.send(result);
            });
        })
        await app.listen(port, () => console.log(`Message received from ${userName}!`));

        await axios.get(`http://localhost:${port}/`)
            .then(response => {
                result = response.data;
            })
            .catch(e => {
                console.log(e);
            });

        await message.reply(result["answer"]);
    }
})

client.login(process.env.DISCORD_BOT_TOKEN)
