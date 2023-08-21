from instagrapi import Client
import time
import datetime



def _login_w_session_id(session_id):
    """Log in to instagram and return instagrapi's Client"""
    cl = Client()
    cl.delay_range = [1, 3]

    print('Logging in ...')
    cl.login_by_sessionid(session_id)

    return cl


def _get_dict_from_message(message) -> dict:
    """ This function get instagrapi's DirectMessage object and
        convert to a dictionary with the same format as JSON file
        when getting data from IG's dump function

    Args:
        message: instagrapi DirectMessage object
    
    Return:
        dictionary containing message detail
        
    """
    msg_dict = {}
    msg_dict['sender_name'] = message.user_id
    msg_dict['timestamp_ms'] = time.mktime(message.timestamp.timetuple()) * 1000
    if message.item_type == 'text':
        msg_dict['content'] = message.text
    elif message.item_type == 'animated_media':
        msg_dict['share'] = {
            'link': message.animated_media['images']['fixed_height']['url'],
        }
    elif message.item_type == 'xma_media_share':
        msg_dict['share'] = {
            'link': str(message.xma_share.video_url)
        }
    elif message.item_type == 'media':
        if message.media.video_url: # video
            msg_dict['videos'] = [] # omit video detail
        else: # image
            msg_dict['photos'] = [] # omit image detail
    elif message.item_type == 'clip': # another kind of video
        msg_dict['videos'] = [] # omit video detail
    elif message.item_type == 'generic_xma':
        msg_dict['photos'] = []
    elif message.item_type == 'voice_media':
        msg_dict['audio_files'] = []
    elif message.item_type == 'video_call_event':
        msg_dict['call_duration'] = None

    if message.reactions:
        reac_list = []
        for reaction in message.reactions['emojis']:
            reac_list.append(
                {
                    "reaction": reaction['emoji'],
                    "actor": reaction['sender_id']
                }
            )
        msg_dict['reactions'] = reac_list

    return msg_dict


def get_dm_from_api(oldest_date: str, session_id: str = None) -> list:
    """Get direct message data back until oldest_date

        Args:
            oldest_date (str): date used as a cutoff to get data newer than this date
            session_id (str): instagram session id. If not specified will use input prompt

        Return:
            A list containing messages from each thread (chat room)

    """

    session_id = session_id if session_id else input('Enter session_id: ')
    cl = _login_w_session_id(session_id)
    oldest_date = datetime.date.fromisoformat(oldest_date)
    thread_idx = 0
    thread_end_flag = False
    threads = cl.direct_threads(10)
    thread_list = []

    while not thread_end_flag:

        # Check if need more threads then update
        if len(threads) < thread_idx + 1:
            print('Getting more thread')
            threads = cl.direct_threads(len(threads) + 10)

        # Stop if can't get more thread
        if len(threads) < thread_idx + 1:
            print('Stopping. No more thread found.')
            thread_end_flag = True
        else: # Otherwise loop to get messages in thread
            thread = threads[thread_idx]
            print('Scraping thread', thread_idx)

            message_idx = 0
            message_end_flag = False
            messages = thread.messages

            # Move to next thread if first message is older than next oldest_date set
            if messages[0].timestamp.date() < oldest_date:
                print('Stopping. Thread too old limit')
                message_end_flag = True
                thread_end_flag = True
            else:
                message_list = []
                while not message_end_flag:
                    # check if need to get more messages
                    if len(messages) < message_idx + 1:
                        # Get 20 more messages
                        messages = cl.direct_messages(thread_id=thread.id,
                                                    amount=len(messages) + 30)
                    
                    # Stop if can't get more messages
                    if len(messages) < message_idx + 1:
                        message_end_flag = True
                    else:
                        message = messages[message_idx]
                        
                        # change thread if reach the oldest_date
                        if message.timestamp.date() < oldest_date:
                            message_end_flag = True
                        else:
                            # reformat to conform with IG's official dump
                            message_dict = _get_dict_from_message(message)   
                            message_list.append(message_dict)
                            message_idx += 1
                
                print(len(message_list), 'messages collected')
                thread_list.append({
                    'message': message_list
                })
                thread_idx += 1
    
    print(len(thread_list), 'threads collected')

    return thread_list


def get_dm_from_zip(path=None) -> list:
    # TODO
    pass
