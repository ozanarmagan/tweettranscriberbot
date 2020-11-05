import time
import tweepy
import praw
import prawcore
from datetime import datetime
#region region yetkilendirme
övgüler = ["iyi bot","cici bot","good bot","nice bot","awesome bot","güzel bot"]
file_path = "bot.log"
auth = tweepy.OAuthHandler("","")
auth.set_access_token("","")
api = tweepy.API(auth)
reddit = praw.Reddit(client_id="",
                     client_secret="",
                     password="",
                     username="tweet_transcriberbot",
                     user_agent="tweettrabscriber  v0.1")
#endregion
#region region definitions
tr_subreddits = ["turkey","KGBTR","yatirim","burdurland","svihs"]
en_subreddits = []
def replypost(url,submission,isenglish):
    try:
        if not "?" in url:
            id = url[url.rindex("/")+1:len(url)]
        elif "?" in url:
            id = url[url.rindex("/") + 1:url.rindex("?")]
        print(id)
        print(submission.url)
        status = api.get_status(id,tweet_mode="extended")
        status.full_text = status.full_text.replace("#","\\#")
        status.full_text = status.full_text.replace("*","\\*")
        status.full_text = status.full_text.replace("_","\\_")
        status.full_text = status.full_text.replace("-","\\-")
        status.full_text = status.full_text.replace("!","\\!")
        status.full_text = status.full_text.replace("'","\\'")
        if not 'media' in status.entities:
            if(status.in_reply_to_user_id == None):
                comment_tr = """Ben posttaki twitter linkinin içeriğini yorum olarak yazan bir botum.
Bu tweet **{name}** [@{screen_name}](https://twitter.com/{screen_name}) tarafından atılmış.  
***    
>{tweet}
***    
^(Eğer seni üzdüysem bana downvote at, bu yorumu kaldırırım:()""".format(name=status.user.name,screen_name=status.user.screen_name,tweet=status.full_text)
                comment_en = """I am a bot that transcribe Twitter links by replying to posts.
This tweet was posted by **{name}** [@{screen_name}](https://twitter.com/{screen_name})  
***    
>{tweet}
***    
^(If I made you sad please downvote me,I will delete this comment:()""".format(name=status.user.name, screen_name=status.user.screen_name, tweet=status.full_text)
            if(status.in_reply_to_user_id != None):
                replied = api.get_status(status.in_reply_to_status_id,tweet_mode="extended")
                comment_tr = """Ben posttaki twitter linkinin içeriğini yorum olarak yazan bir botum.
Bu tweet **{name}** [@{screen_name}](https://twitter.com/{screen_name}) tarafından atılmış.  
***    
>{tweet}
***    
Bu tweet  {replied_user} [@{replied_user_screen}](https://twitter.com/{replied_user_screen}) adlı kullanıcının aşağıdaki tweetine yanıt olarak atıldı
***
>{tweet_replied}
***
^(Eğer seni üzdüysem bana downvote at,bu yorumu silerim)""".format(name=status.user.name, screen_name=status.user.screen_name, tweet=status.full_text,replied_user=replied.user.name,replied_user_screen=replied.user.screen_name,tweet_replied=replied.full_text)
                comment_en = """I am a bot that transcribe Twitter links by replying to posts.
This tweet was posted by **{name}** [@{screen_name}](https://twitter.com/{screen_name})  
***    
>{tweet}
***    
This tweet is a reply to {replied_user} [@{replied_user_screen}](https://twitter.com/{replied_user_screen})'s this tweet
***
>{tweet_replied}
***
^(If I made you sad please downvote me,I will delete this comment:()""".format(name=status.user.name, screen_name=status.user.screen_name, tweet=status.full_text,
                               replied_user=replied.user.name, replied_user_screen=replied.user.screen_name,
                               tweet_replied=replied.full_text)
            if(status.is_quote_status == True):
                quoted_status = api.get_status(status.quoted_status_id_str,tweet_mode="extended")
                comment_tr = """Ben posttaki twitter linkinin içeriğini yorum olarak yazan bir botum.
Bu tweet **{name}** [@{screen_name}](https://twitter.com/{screen_name}) tarafından atılmış.  
***    
>{tweet}
***    
Bu tweet  **{quoted_user}** [@{quoted_user_screen}](https://twitter.com/{quoted_user_screen}) adlı kullanıcının aşağıdaki tweetine alıntı yapılarak atıldı
***
>{tweet_quoted}
***
^(Eğer seni üzdüysem bana downvote at,bu yorumu kaldırırım :()""".format(name=status.user.name, screen_name=status.user.screen_name, tweet=status.full_text,
                   quoted_user=quoted_status.user.name, quoted_user_screen=quoted_status.user.screen_name,
                   tweet_quoted=quoted_status.full_text)
                comment_en = """I am a bot that transcribe Twitter links by replying to posts.
This tweet was posted by **{name}** [@{screen_name}](https://twitter.com/{screen_name})  
***    
>{tweet}
***    
This tweet is quoted **{quoted_user}** [@{quoted_user_screen}](https://twitter.com/{quoted_user_screen})'s following tweet
***
>{tweet_quoted}
***
^(If I made you sad please downvote me,I will delete this comment:()""".format(name=status.user.name, screen_name=status.user.screen_name, tweet=status.full_text,
                   quoted_user=quoted_status.user.name,quoted_user_screen=quoted_status.user.screen_name,
                   tweet_quoted=quoted_status.full_text)
            if(isenglish == True):
                submission.reply(comment_en)
                submission.save()
                print("""[{time}]Yorum yapıldı. URL: {url} Dil:EN""".format(time=datetime.now().strftime("%H:%M:%S"),url=submission.shortlink))
            elif(isenglish == False):
                submission.reply(comment_tr)
                submission.save()
                print("""[{time}]Yorum yapıldı. URL: {url} Dil:TR""".format(time=datetime.now().strftime("%H:%M:%S"), url=submission.shortlink))
        photourls = []
        isvideo = False
        videourl = ""
        if 'media' in status.entities:
            if status.extended_entities == None:
                for image in status.entities['media']:
                    if image['type'] == "photo":
                        photourls.append(image['media_url'])
            if not status.extended_entities == None:

                for image in status.extended_entities['media']:
                    if image['type'] == "video":
                        isvideo = True
                        max_bitrate = 0
                        var_index = 0
                        for variant in image['video_info']['variants']:
                            if variant['content_type'] == "video/mp4":
                                if int(variant['bitrate']) > max_bitrate:
                                    max_bitrate = int(variant['bitrate'])
                                    videourl = variant['url']
                    if image['type'] == "photo":
                        photourls.append(image['media_url'])
            if isvideo == True:
                if (status.in_reply_to_user_id == None):
                    comment_tr = """Ben posttaki twitter linkinin içeriğini yorum olarak yazan bir botum.
Bu tweet **{name}** [@{screen_name}](https://twitter.com/{screen_name}) tarafından atılmış.  
***    
>{tweet}
[Tweete Eklenen Video]({media_url})
***    
^(Eğer seni üzdüysem bana downvote at, bu yorumu kaldırırım:()""".format(name=status.user.name,
                                                                                         screen_name=status.user.screen_name,
                                                                                         tweet=status.full_text,media_url=videourl)
                    comment_en = """I am a bot that transcribe Twitter links by replying to posts.
This tweet was posted by **{name}** [@{screen_name}](https://twitter.com/{screen_name})  
***    
>{tweet}
[Attached video]({media_url})
***    
^(If I made you sad please downvote me,I will delete this comment:()""".format(name=status.user.name,
                                                                                               screen_name=status.user.screen_name,
                                                                                               tweet=status.full_text,media_url=videourl)
                if (status.in_reply_to_user_id != None):
                    replied = api.get_status(status.in_reply_to_status_id,tweet_mode="extended")
                    comment_tr = """Ben posttaki twitter linkinin içeriğini yorum olarak yazan bir botum.
Bu tweet **{name}** [@{screen_name}](https://twitter.com/{screen_name}) tarafından atılmış.  
***    
>{tweet}
[Tweete Eklenen Video]({media_url})
***    
Bu tweet  {replied_user} [@{replied_user_screen}](https://twitter.com/{replied_user_screen}) adlı kullanıcının aşağıdaki tweetine yanıt olarak atıldı
***
>{tweet_replied}
***
^(Eğer seni üzdüysem bana downvote at,bu yorumu silerim)""".format(name=status.user.name,
                                                                                   screen_name=status.user.screen_name,
                                                                                   tweet=status.full_text,
                                                                                   replied_user=replied.user.name,
                                                                                   replied_user_screen=replied.user.screen_name,
                                                                                   tweet_replied=replied.full_text,media_url=videourl)
                    comment_en = """I am a bot that transcribe Twitter links by replying to posts.
This tweet was posted by **{name}** [@{screen_name}](https://twitter.com/{screen_name})  
***    
>{tweet}
[Attached video]({media_url})
***    
This tweet is a reply to {replied_user} [@{replied_user_screen}](https://twitter.com/{replied_user_screen})'s this tweet
***
>{tweet_replied}
***
^(If I made you sad please downvote me,I will delete this comment:()""".format(name=status.user.name,
                                                                                               screen_name=status.user.screen_name,
                                                                                               tweet=status.full_text,
                                                                                               replied_user=replied.user.name,
                                                                                               replied_user_screen=replied.user.screen_name,
                                                                                               tweet_replied=replied.full_text,media_url=videourl)
                if (status.is_quote_status == True):
                    quoted_status = api.get_status(status.quoted_status_id_str,tweet_mode="extended")
                    comment_tr = """Ben posttaki twitter linkinin içeriğini yorum olarak yazan bir botum.
Bu tweet **{name}** [@{screen_name}](https://twitter.com/{screen_name}) tarafından atılmış.  
***    
>{tweet}
[Tweete Eklenen Video]({media_url})
***    
Bu tweet  **{quoted_user}** [@{quoted_user_screen}](https://twitter.com/{quoted_user_screen}) adlı kullanıcının aşağıdaki tweetine alıntı yapılarak atıldı
***
>{tweet_quoted}
***
^(Eğer seni üzdüysem bana downvote at,bu yorumu kaldırırım :()""".format(name=status.user.name,
                                                                                         screen_name=status.user.screen_name,
                                                                                         tweet=status.full_text,
                                                                                         quoted_user=quoted_status.user.name,
                                                                                         quoted_user_screen=quoted_status.user.screen_name,
                                                                                         tweet_quoted=quoted_status.full_text,media_url=videourl)
                    comment_en = """I am a bot that transcribe Twitter links by replying to posts.
This tweet was posted by **{name}** [@{screen_name}](https://twitter.com/{screen_name})  
***    
>{tweet}
[Attached video]({media_url})
***    
This tweet is quoted **{quoted_user}** [@{quoted_user_screen}](https://twitter.com/{quoted_user_screen})'s following tweet
***
>{tweet_quoted}
***
^(If I made you sad please downvote me,I will delete this comment:()""".format(name=status.user.name,
                                                                                               screen_name=status.user.screen_name,
                                                                                               tweet=status.full_text,
                                                                                               quoted_user=quoted_status.user.name,
                                                                                               quoted_user_screen=quoted_status.user.screen_name,
                                                                                               tweet_quoted=quoted_status.full_text,media_url=videourl)
            if isvideo == False:
                photostring_tr = ""
                photostring_en = ""
                index = 1
                for photo in photourls:
                    photostring_tr = photostring_tr + "[Eklenen görsel "+ str(index) + "]("+photo+") "
                    photostring_en = photostring_en + "[Attached photo "+ str(index) + "]("+photo+") "
                    index = index + 1
                if (status.in_reply_to_user_id == None):
                        comment_tr = """Ben posttaki twitter linkinin içeriğini yorum olarak yazan bir botum.
Bu tweet **{name}** [@{screen_name}](https://twitter.com/{screen_name}) tarafından atılmış.  
***    
>{tweet}
{media_url}
***    
^(Eğer seni üzdüysem bana downvote at, bu yorumu kaldırırım:()""".format(name=status.user.name,
                                                                                         screen_name=status.user.screen_name,
                                                                                         tweet=status.full_text,
                                                                                         media_url=photostring_tr)
                        comment_en = """I am a bot that transcribe Twitter links by replying to posts.
This tweet was posted by **{name}** [@{screen_name}](https://twitter.com/{screen_name})  
***    
>{tweet}
{media_url}
***    
^(If I made you sad please downvote me,I will delete this comment:()""".format(name=status.user.name,
                                                                                               screen_name=status.user.screen_name,
                                                                                               tweet=status.full_text,
                                                                                               media_url=photostring_en)
                if (status.in_reply_to_user_id != None):
                        replied = api.get_status(status.in_reply_to_status_id,tweet_mode="extended")
                        comment_tr = """Ben posttaki twitter linkinin içeriğini yorum olarak yazan bir botum.
Bu tweet **{name}** [@{screen_name}](https://twitter.com/{screen_name}) tarafından atılmış.  
***    
>{tweet}
{media_url}
***    
Bu tweet  {replied_user} [@{replied_user_screen}](https://twitter.com/{replied_user_screen}) adlı kullanıcının aşağıdaki tweetine yanıt olarak atıldı
***
>{tweet_replied}
***
^(Eğer seni üzdüysem bana downvote at,bu yorumu silerim)""".format(name=status.user.name,
                                                                                   screen_name=status.user.screen_name,
                                                                                   tweet=status.full_text,
                                                                                   replied_user=replied.user.name,
                                                                                   replied_user_screen=replied.user.screen_name,
                                                                                   tweet_replied=replied.full_text,
                                                                                   media_url=photostring_tr)
                        comment_en = """I am a bot that transcribe Twitter links by replying to posts.
This tweet was posted by **{name}** [@{screen_name}](https://twitter.com/{screen_name})  
***    
>{tweet}
{media_url}
***    
This tweet is a reply to {replied_user} [@{replied_user_screen}](https://twitter.com/{replied_user_screen})'s this tweet
***
>{tweet_replied}
***
^(If I made you sad please downvote me,I will delete this comment:()""".format(name=status.user.name,
                                                                                               screen_name=status.user.screen_name,
                                                                                               tweet=status.full_text,
                                                                                               replied_user=replied.user.name,
                                                                                               replied_user_screen=replied.user.screen_name,
                                                                                               tweet_replied=replied.full_text,
                                                                                               media_url=photostring_en)
                if (status.is_quote_status == True):
                        quoted_status = api.get_status(status.quoted_status_id_str,tweet_mode="extended")
                        comment_tr = """Ben posttaki twitter linkinin içeriğini yorum olarak yazan bir botum.
Bu tweet **{name}** [@{screen_name}](https://twitter.com/{screen_name}) tarafından atılmış.  
***    
>{tweet}
{media_url}
***    
Bu tweet  **{quoted_user}** [@{quoted_user_screen}](https://twitter.com/{quoted_user_screen}) adlı kullanıcının aşağıdaki tweetine alıntı yapılarak atıldı
***
>{tweet_quoted}
***
^(Eğer seni üzdüysem bana downvote at,bu yorumu kaldırırım :()""".format(name=status.user.name,
                                                                                         screen_name=status.user.screen_name,
                                                                                         tweet=status.full_text,
                                                                                         quoted_user=quoted_status.user.name,
                                                                                         quoted_user_screen=quoted_status.user.screen_name,
                                                                                         tweet_quoted=quoted_status.full_text,
                                                                                         media_url=photostring_tr)
                        comment_en = """I am a bot that transcribe Twitter links by replying to posts.
This tweet was posted by **{name}** [@{screen_name}](https://twitter.com/{screen_name})  
***    
>{tweet}
{media_url}
***    
This tweet is quoted **{quoted_user}** [@{quoted_user_screen}](https://twitter.com/{quoted_user_screen})'s following tweet
***
>{tweet_quoted}
***
^(If I made you sad please downvote me,I will delete this comment:()""".format(name=status.user.name,
                                                                                               screen_name=status.user.screen_name,
                                                                                               tweet=status.full_text,
                                                                                               quoted_user=quoted_status.user.name,
                                                                                               quoted_user_screen=quoted_status.user.screen_name,
                                                                                               tweet_quoted=quoted_status.full_text,
                                                                                               media_url=photostring_en)
            if(isenglish == True):
                    submission.reply(comment_en)
                    submission.save()
                    print("""[{time}]Yorum yapıldı. URL: {url} Dil:EN""".format(time=datetime.now().strftime("%H:%M:%S"),url=submission.shortlink))
                    f = open(file_path,'a')
                    f.write("""\n[{time}]Yorum yapıldı. URL: {url} Dil:EN""".format(time=datetime.now().strftime("%H:%M:%S"), url=submission.shortlink))
                    f.close()
            elif(isenglish == False):
                    submission.reply(comment_tr)
                    submission.save()
                    print("""[{time}]Yorum yapıldı. URL: {url} Dil:TR""".format(time=datetime.now().strftime("%H:%M:%S"), url=submission.shortlink))
                    f = open(file_path,'a')
                    f.write("""\n[{time}]Yorum yapıldı. URL: {url} Dil:TR""".format(time=datetime.now().strftime("%H:%M:%S"), url=submission.shortlink))
                    f.close()

    except tweepy.TweepError as e:
        print("""[{time}]Posta yorum atılmadı.URL: {url} Tweet: {tweet} """.format(time=datetime.now().strftime("%H:%M:%S"),url=submission.shortlink,tweet=url))
        print(e)
        if str(e.api_code) == "144":
            submission.save()
        f = open(file_path,'a')
        f.write("""\n[{time}]Posta yorum atılmadı.URL: {url} Tweet: {tweet} """.format(time=datetime.now().strftime("%H:%M:%S"),url=submission.shortlink,tweet=url))
        f.write(str(e))
        f.close()
    except praw.exceptions.RedditAPIException as ex:
        print("""[{time}]Posta yorum atılmadı.URL: {url} Tweet: {tweet} """.format(time=datetime.now().strftime("%H:%M:%S"),url=submission.shortlink,tweet=url))
        f = open(file_path, 'a')
        f.write("""\n[{time}]Posta yorum atılmadı.URL: {url} Tweet: {tweet} """.format(time=datetime.now().strftime("%H:%M:%S"),url=submission.shortlink, tweet=url))
        f.write(str(ex))
        f.close()
    except prawcore.exceptions.Forbidden as ex:
        print("""[{time}]Posta yorum atılmadı.URL: {url} Tweet: {tweet} """.format(time=datetime.now().strftime("%H:%M:%S"),url=submission.shortlink,tweet=url))
        f = open(file_path, 'a')
        f.write("""\n[{time}]Posta yorum atılmadı.URL: {url} Tweet: {tweet} """.format(time=datetime.now().strftime("%H:%M:%S"),url=submission.shortlink, tweet=url))
        f.write(str(ex))
        f.close()

def replycomment(comment,isenglish):
    try:
        submission = comment.submission
        url = submission.url
        id = url[url.rindex("/") + 1:len(url)]
        mediastring_tr = ""
        mediastring_en = ""
        status = api.get_status(id,tweet_mode="extended")
        if 'media' in status.entities:
            index = 1
            entityadded = False
            if not status.extended_entities == None:
                for image in status.extended_entities['media']:
                    if image['type'] == "video":
                        isvideo = True
                        max_bitrate = 0
                        var_index = 0
                        for variant in image['video_info']['variants']:
                            if variant['content_type'] == "video/mp4":
                                if int(variant['bitrate']) > max_bitrate:
                                    max_bitrate = int(variant['bitrate'])
                                    mediastring_tr = mediastring_tr + "[Tweete Eklenen Video](" + variant['url'] + ")"
                                    mediastring_en = mediastring_en + "[Attached Video](" + variant['url'] + ") "
                    if image['type'] == "photo":
                        if entityadded == False:
                            for image in status.entities['media']:
                                mediastring_tr = mediastring_tr + "[Tweete Eklenen Görsel " + str(index) + "](" + status.entities['media'][0]['media_url'] + ") "
                                mediastring_en = mediastring_en + "[Attached Photo " + str(index) + "](" + status.entities['media'][0]['media_url'] + ") "
                                index = index + 1
                                entityadded = True
                        mediastring_tr = mediastring_tr + "[Tweete Eklenen Görsel " + str(index) + "](" + image[
                            'media_url'] + ") "
                        mediastring_en = mediastring_en + "[Attached Photo " + str(index) + "](" + image[
                            'media_url'] + ") "
                        index = index + 1
            if status.extended_entities == None:
                mediastring_tr = mediastring_tr + "[Tweete Eklenen Görsel " + str(index) + "](" + status.entities['media']['media_url'] + ") "
                mediastring_en = mediastring_en + "[Attached Photo " + str(index) + "](" + status.entities['media']['media_url'] + ") "
        if (status.in_reply_to_user_id == None):
            comment_tr = """Beni mentionladığın için teşekkür ederim.
Ben posttaki twitter linkinin içeriğini yorum olarak yazan bir botum.
Bu posttaki tweet **{name}** [@{screen_name}](https://twitter.com/{screen_name}) tarafından atılmış.  
***    
>{tweet}
{media_string}
***    
^(Seni üzdüysem bana downvote at,yorumu kaldırırım :()""".format(name=status.user.name, screen_name=status.user.screen_name, tweet=status.full_text,media_string=mediastring_tr)
            comment_en = """Thanks for mentioning me.
I am a bot that transcribe Twitter links by replying to posts.
Tweet in this post was posted by **{name}** [@{screen_name}](https://twitter.com/{screen_name})  
***    
>{tweet}
{media_string}
***    
^(If I made you sad please downvote me,I will delete this reply then :()""".format(name=status.user.name, screen_name=status.user.screen_name, tweet=status.full_text,media_string=mediastring_en)
        if (status.in_reply_to_user_id != None):
            replied = api.get_status(status.in_reply_to_status_id)
            comment_tr = """Beni mentionladığın için teşekkür ederim.
Ben posttaki twitter linkinin içeriğini yorum olarak yazan bir botum.
Bu posttaki tweet **{name}** [@{screen_name}](https://twitter.com/{screen_name}) tarafından atılmış.  
***    
>{tweet}
{media_string}
***    
Bu tweet  {replied_user} [@{replied_user_screen}](https://twitter.com/{replied_user_screen}) adlı kullanıcının aşağıdaki tweetine yanıt olarak atıldı
***
>{tweet_replied}
***
^(Eğer seni üzdüysem bana downvote at,yorumu silerim :()""".format(name=status.user.name, screen_name=status.user.screen_name, tweet=status.full_text,
            replied_user=replied.user.name, replied_user_screen=replied.user.screen_name, tweet_replied=replied.full_text,media_string=mediastring_tr)
            comment_en = """Thanks for mentioning me.
I am a bot that transcribe Twitter links by replying to posts.
Linked tweet in this post was posted by **{name}** [@{screen_name}](https://twitter.com/{screen_name})  
***    
>{tweet}
{media_string}
***    
This tweet is a reply to {replied_user} [@{replied_user_screen}](https://twitter.com/{replied_user_screen})'s this tweet
***
>{tweet_replied}
***
^(If I made you sad please downvote me,I will delete this reply then :()""".format(name=status.user.name, screen_name=status.user.screen_name, tweet=status.full_text,
            replied_user=replied.user.name, replied_user_screen=replied.user.screen_name,
            tweet_replied=replied.full_text,media_string=mediastring_en)
        if (status.is_quote_status == True):
            quoted_status = api.get_status(status.quoted_status_id_str)
            comment_tr = """Ben posttaki twitter linkinin içeriğini yorum olarak yazan bir botum.
Bu tweet **{name}** [@{screen_name}](https://twitter.com/{screen_name}) tarafından atılmış.  
***    
>{tweet}
{media_string}
***    
Bu tweet  **{quoted_user}** [@{quoted_user_screen}](https://twitter.com/{quoted_user_screen}) adlı kullanıcının aşağıdaki tweetine alıntı yapılarak atıldı
***
>{tweet_quoted}
***
^(Eğer seni üzdüysem bana downvote at,bu yorumu silerim :()""".format(name=status.user.name, screen_name=status.user.screen_name, tweet=status.full_text,
            quoted_user=quoted_status.user.name, quoted_user_screen=quoted_status.user.screen_name,
            tweet_quoted=quoted_status.full_text,media_string=mediastring_tr)
            comment_en = """I am a bot that transcribe Twitter links by replying to posts.
This tweet was posted by **{name}** [@{screen_name}](https://twitter.com/{screen_name})  
***    
>{tweet}
{media_string}
***    
This tweet is quoted **{quoted_user}** [@{quoted_user_screen}](https://twitter.com/{quoted_user_screen})'s following tweet
***
>{tweet_quoted}
***
^(If I made you sad please downvote me,I will delete this reply then :()""".format(name=status.user.name, screen_name=status.user.screen_name, tweet=status.full_text,
        quoted_user=quoted_status.user.name, quoted_user_screen=quoted_status.user.screen_name,
        tweet_quoted=quoted_status.full_text,media_string=mediastring_en)
        if (isenglish == True):
            övgümü = False
            for övgü in övgüler:
                if övgü in comment.body:
                    övgümü = True
                    comment.reply("Thank you ♥")
                    print("""[{time}]Mentiona yanıt verildi. URL: {url} Dil:EN""".format(time=datetime.now().strftime("%H:%M:%S"),
                                                                    url=submission.shortlink))
                    f = open(file_path,'a')
                    f.write("""\n[{time}]Mentiona yanıt verildi. URL: {url} Dil:EN""".format(time=datetime.now().strftime("%H:%M:%S"),
                                                                    url=submission.shortlink))
                    f.close()
            if not comment.submission.saved:
                if övgümü == False:
                    comment.reply(comment_en)
                    comment.submission.save()
                    print("""[{time}]Mentiona yanıt verildi. URL: {url} Dil:EN""".format(time=datetime.now().strftime("%H:%M:%S"),
                                                                    url=submission.shortlink))
                    f = open(file_path,'a')
                    f.write("""\n[{time}]Mentiona yanıt verildi. URL: {url} Dil:EN""".format(time=datetime.now().strftime("%H:%M:%S"),
                                                                    url=submission.shortlink))
                    f.close()
        elif (isenglish == False):
            övgümü = False
            for övgü in övgüler:
                if övgü in comment.body:
                    övgümü = True
                    comment.reply("Teşekkürler ♥")
                    print("""[{time}]Mentiona yanıt verildi. URL: {url} Dil:TR""".format(time=datetime.now().strftime("%H:%M:%S"),
                                                                    url=submission.shortlink))
                    f = open(file_path,'a')
                    f.write("""\n[{time}]Mentiona yanıt verildi. URL: {url} Dil:TR""".format(time=datetime.now().strftime("%H:%M:%S"),
                                                                    url=submission.shortlink))
                    f.close()
            if not comment.submission.saved:
                if övgümü == False:
                    comment.reply(comment_tr)
                    comment.submission.save()
                    print("""[{time}]Mentiona yanıt verildi. URL: {url} Dil:TR""".format(time=datetime.now().strftime("%H:%M:%S"),
                                                                    url=submission.shortlink))
                    f = open(file_path,'a')
                    f.write("""\n[{time}]Mentiona yanıt verildi. URL: {url} Dil:TR""".format(time=datetime.now().strftime("%H:%M:%S"),
                                                                    url=submission.shortlink))
                    f.close()
    except tweepy.TweepError as e:
        if isenglish==True:
            comment.reply("""Thanks for mentioning me.
Unfortunately,I couldn't find the tweet whis is linked in this post.Maybe it is deleted?
***
^(If I made you sad please downvote me,I will delete this reply)""")
            print("""[{time}]Tweet Bulunamadı.Mentiona yanıt verildi. URL: {url} Dil:EN""".format(time=datetime.now().strftime("%H:%M:%S"),
                                                                    url=submission.shortlink))
            print(e)
            if str(e.code) == "144":
                comment.submission.save()
            f = open(file_path,'a')
            f.write("""\n[{time}]Tweet Bulunamadı.Mentiona yanıt verildi. URL: {url} Dil:EN""".format(
                time=datetime.now().strftime("%H:%M:%S"),
                url=submission.shortlink))
            f.write(str(e))
            f.close()
        elif isenglish==False:
            comment.reply("""Beni mentionladığın için teşekkür ederim.
Ne yazık ki posttaki tweeti bulamadım.Belki silinmiştir?
***
^(Eğer seni üzdüysem bana downvote at,yorumu kaldırırım)""")
            print("""[{time}]Tweet Bulunamadı.Mentiona yanıt verildi. URL: {url} Dil:TR""".format(time=datetime.now().strftime("%H:%M:%S"),
                                                                    url=submission.shortlink))
            f = open(file_path,'a')
            f.write("""\n[{time}]Tweet Bulunamadı.Mentiona yanıt verildi. URL: {url} Dil:TR""".format(time=datetime.now().strftime("%H:%M:%S"),
                                                                    url=submission.shortlink))
            f.close()
#endregion
while True:
    try:
        for mention in reddit.inbox.unread():

            istur = True
            if "twitter.com" in mention.submission.url:
                for sub in en_subreddits:
                    if sub == mention.submission.subreddit:
                        istur = False
                if istur == True:
                    replycomment(mention,False)
                    mention.mark_read()
                elif istur == False:
                    replycomment(mention,True)
                    mention.mark_read()
            else:
                if istur == True:
                    mention.reply("""Beni mentionladığın için teşekkür ederim.
Bu postta bir twitter linki bulamadım :(
***
^(Eğer seni üzdüysem beni downvotela,bu yorumu silerim:()""")
                    mention.mark_read()
                    print("""[{time}]Postta Tweet Bulunamadı.Mentiona yanıt verildi. URL: {url} Dil:TR""".format(time=datetime.now().strftime("%H:%M:%S"),url=mention.submission.shortlink))
                    f = open(file_path,'a')
                    f.write("""\n[{time}]Postta Tweet Bulunamadı.Mentiona yanıt verildi.URL: {url} Dil:TR""".format(
                    time=datetime.now().strftime("%H:%M:%S"),
                    url=mention.submission.shortlink))
                    f.close()
                elif istur == False:
                    mention.reply("""Thanks for mentioning me.
I couldn't find any Twitter link in this post:(
***
^(If I made you sad please downvote me,I will delete this comment:()""")
                    mention.mark_read()
                    print("""[{time}]Postta Tweet Bulunamadı.Mentiona yanıt verildi.URL: {url} Dil:EN""".format(
                    time=datetime.now().strftime("%H:%M:%S"),
                    url=mention.submission.shortlink))
                    f = open(file_path,'a')
                    f.write("""\n[{time}]Postta Tweet Bulunamadı.Mentiona yanıt verildi.URL: {url} Dil:EN""".format(
                    time=datetime.now().strftime("%H:%M:%S"),
                    url=mention.submission.shortlink))
                    f.close()
    except praw.exceptions.RedditAPIException as e:
        print("""[{time}]Mention kontrol ederken Hata oldu.""".format(time=datetime.now().strftime("%H:%M:%S")))
        f = open(file_path,'a')
        f.write("""\n[{time}]Mention kontrol ederken Hata oldu.""".format(time=datetime.now().strftime("%H:%M:%S")))
        f.close()
    print("Mentionlar kontrol edildi")
    try:
        for sub in tr_subreddits:
            subreddit = reddit.subreddit(sub)
            for submisson in subreddit.hot(limit=25):

                if "twitter.com" in submisson.url:
                    if not submisson.saved:
                        replypost(submisson.url,submisson,False)
            for submisson in subreddit.new(limit=25):

                if "twitter.com" in submisson.url:
                    if not submisson.saved:
                        replypost(submisson.url,submisson,False)

        for sub in en_subreddits:
            subreddit = reddit.subreddit(sub)
            for submission in subreddit.hot(limit=25):

                if "twitter.com" in submission.url:
                    if not submission.saved:
                        replypost(submission.url,submission,True)
            for submission in subreddit.new():
                if "twitter.com" in submission.url:
                    if not submission.saved:
                        replypost(submission.url,submission,True)

    except praw.exceptions.RedditAPIException as e:
        print("""[{time}]Subreddit kontrol ederken Hata oldu.""".format(time=datetime.now().strftime("%H:%M:%S")))
        print(e)
        f = open(file_path,'a')
        f.write("""\n[{time}]Subreddit kontrol ederken Hata oldu.""".format(time=datetime.now().strftime("%H:%M:%S")))
        f.write(str(e))
        f.close()
    print("Subredditler kontrol edildi")
    try:
        for comment in reddit.redditor(reddit.user.me().name).comments.new(limit=None):
            if comment.score < 1:
                comment.delete()
                print("""[{time}Yorum silindi Sebep:Downvote.""".format(
                    time=datetime.now().strftime("%H:%M:%S")))
                f = open(file_path,'a')
                f.write("""\n[{time}Yorum silindi Sebep:Downvote.""".format(
                    time=datetime.now().strftime("%H:%M:%S")))
                f.close()
    except praw.exceptions.RedditAPIException as e:
        print("""[{time}Yorumlarımı kontrol ederken Hata oldu.""".format(time=datetime.now().strftime("%H:%M:%S")))
        f = open(file_path,'a')
        f.write("""\n[{time}Yorumlarımı kontrol ederken Hata oldu.""".format(time=datetime.now().strftime("%H:%M:%S")))
        f.write(str(e))
        f.close()
        print(e)
    print("Yorumlarım kontrol edildi")
    time.sleep(15)
