require('dotenv').config()
const { Client } = require('discord.js')
const client = new Client()

client.on('ready', () => {
    console.log(`Logged in as ${client.user.tag}!`)
})

client.on('message', async message => {
    const splitMessage = message.content.split(' ')

    if (splitMessage[0] === '$speckle-bot') {
        const command = splitMessage[1]

        if (!command) {
            return
        }

        if (command.toLowerCase() === 'hello') {
            await message.reply("Hello from speckle-bot and return name team!")
        }
    }
})

client.login(process.env.DISCORD_BOT_TOKEN)