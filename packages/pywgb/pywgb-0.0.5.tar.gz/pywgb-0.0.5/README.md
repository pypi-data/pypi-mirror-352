# pywgb
Wecom(A.K.A. WeChat Work) Group Bot python API.

## Homepage

> [ChowRex/pywgb: Wecom(A.K.A Wechat Work) Group Bot python API.](https://github.com/ChowRex/pywgb)

## How to use

1. Create a [Wecom Group Bot](https://qinglian.tencent.com/help/docs/2YhR-6/).

2. Copy the webhook URL or just the `key`. It should be like:

   - `Webhook`: *https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=UUID*
   - `Key`: *UUID*

3. Install this package: 

    ```bash
    pip install -U pywgb
    ```

4. Refer code below:

   ```python
   from pywgb import TextWeComGroupBot, MarkdownWeComGroupBot, ImageWeComGroupBot, NewsWeComGroupBot, FileWeComGroupBot, VoiceWeComGroupBot
   
   KEY = "PASTE_YOUR_KEY_OR_WEBHOOKURL_HERE"
   
   # If you want to send Text message, use this.
   msg = "This is a test Text message."
   bot = TextWeComGroupBot(KEY)
   bot.send(msg)
   
   # If you want to send Markdown message, use this.
   msg = "# This is a test Markdown title message."
   bot = MarkdownWeComGroupBot(KEY)
   bot.send(msg)
   
   # If you want to send Image message, use this.
   file = "Path/To/Your/Image.png" or "Path/To/Your/Image.jpg"
   bot = ImageWeComGroupBot(KEY)
   bot.send(file_path=file)
   
   # If you want to send News message, use this.
   articles = [
       {
           "title": "This is a test news",
           "description": "You can add description here",
           "url":  # Here is the link of picture
               "www.tencent.com",
           "picurl": "https://www.tencent.com/img/index/tencent_logo.png"
       },
   ]
   bot = NewsWeComGroupBot(KEY)
   bot.send(articles=articles)
   
   # If you want to send File message, use this.
   file = "Path/To/Your/File.suffix"
   bot = FileWeComGroupBot(KEY)
   bot.send(file_path=file)
   
   # If you want to send Voice message, use this.
   file = "Path/To/Your/Voice.amr"  # BE ADVISED: ONLY support amr file
   bot = VoiceWeComGroupBot(KEY)
   bot.send(file_path=file)
   
   ```

## Official Docs

> Only Chinese version doc: [群机器人配置说明 - 文档 - 企业微信开发者中心](https://developer.work.weixin.qq.com/document/path/99110)

## Roadmap

- [x] v0.0.1: 🎉 Initial project. Offering send `Text` and `Markdown` type message.
- [x] v0.0.2: 🖼️ Add `Image` type message support;
  
  - Add overheat detect function and unified exception handling
- [x] v0.0.3: 📰 Add `News` type message support;

  - Move bots into a new module: `bot`
- [x] v0.0.4: 📂 Add `File` type message support;

    - Refactor `bot` module
- [x] v0.0.5: 🗣️ Add `Voice` type message support.
    - Refactor `deco` module
    - Add `verify_file` decorator
    - Introverted parameters check errors
    - Add more content into README.md
- [ ] v0.0.6: 🗒️ Add `TextCard` type message support.
- [ ] v0.0.7: 🗃️ Add `PictureCard` type message support.
- [ ] v0.1.0: 👍 First FULL capacity stable version release.Fix bugs and so on.

