import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from app.api.v1.endpoints.chats import _build_chat_response
from app.db.models.chats import Chat
from app.db.models.users import User
from app.db.models.messages import Message


def make_db_side_effect(*mocks):
    """Хелпер: возвращает side_effect список для mock_db.execute"""
    return list(mocks)


# ---------------------------------------------------------------------------
# Вспомогательная фабрика для приватного чата
# ---------------------------------------------------------------------------

def _make_private_chat_mocks(
    current_user_id,
    other_user_id,
    other_username="otheruser",
    avatar_url=None,
    last_msg_content="Hello",
    last_msg_created_at=None,
    last_read_message_id=None,
    total_count=3,
    other_user_exists=True,
):
    """
    Возвращает (chat, side_effects) для приватного чата.
    side_effects — список из 5 моков для db.execute в правильном порядке.
    """
    chat = MagicMock(spec=Chat)
    chat.id = str(uuid4())
    chat.type = "private"

    # 1. Участники
    participants_result = MagicMock()
    participants_result.scalars.return_value.all.return_value = (
        [current_user_id, other_user_id] if other_user_exists else [current_user_id]
    )

    # 2. Другой пользователь
    user_result = MagicMock()
    if other_user_exists:
        mock_user = MagicMock(spec=User)
        mock_user.username = other_username
        mock_user.avatar_url = avatar_url
        user_result.scalar_one_or_none.return_value = mock_user
    else:
        user_result.scalar_one_or_none.return_value = None

    # 3. Последнее сообщение
    last_msg_result = MagicMock()
    if last_msg_content is not None:
        last_msg = MagicMock(spec=Message)
        last_msg.content = last_msg_content
        last_msg.created_at = last_msg_created_at
        last_msg_result.scalar_one_or_none.return_value = last_msg
    else:
        last_msg_result.scalar_one_or_none.return_value = None

    # 4. Участник (для непрочитанных)
    part = MagicMock()
    part.last_read_message_id = last_read_message_id
    part_result = MagicMock()
    part_result.scalar_one_or_none.return_value = part

    # 5. Счётчик сообщений
    count_result = MagicMock()
    count_result.scalar_one.return_value = total_count

    side_effects = [participants_result, user_result, last_msg_result, part_result, count_result]
    return chat, side_effects


# ===========================================================================
# ПРИВАТНЫЙ ЧАТ
# ===========================================================================

@pytest.mark.asyncio
async def test_build_chat_response_private():
    """Базовый кейс: приватный чат с сообщением и непрочитанными"""
    mock_db = AsyncMock()
    current_user_id = str(uuid4())
    other_user_id = str(uuid4())

    chat, side_effects = _make_private_chat_mocks(
        current_user_id=current_user_id,
        other_user_id=other_user_id,
        other_username="otheruser",
        last_msg_content="Hello",
        total_count=3,
    )
    mock_db.execute.side_effect = side_effects

    result = await _build_chat_response(chat, current_user_id, mock_db)

    assert result.name == "otheruser"
    assert result.unread_count == 3
    assert result.last_message == "Hello"
    assert result.type == "private"


@pytest.mark.asyncio
async def test_build_chat_response_private_no_messages():
    """Приватный чат без сообщений — last_message должен быть None, unread_count=0"""
    mock_db = AsyncMock()
    current_user_id = str(uuid4())
    other_user_id = str(uuid4())

    chat, side_effects = _make_private_chat_mocks(
        current_user_id=current_user_id,
        other_user_id=other_user_id,
        last_msg_content=None,   # нет сообщений
        total_count=0,
    )
    mock_db.execute.side_effect = side_effects

    result = await _build_chat_response(chat, current_user_id, mock_db)

    assert result.last_message is None
    assert result.last_message_time is None
    assert result.unread_count == 0


@pytest.mark.asyncio
async def test_build_chat_response_private_other_user_not_found():
    """Собеседник не найден — имя должно быть 'Unknown' или 'Chat'"""
    mock_db = AsyncMock()
    current_user_id = str(uuid4())

    chat, side_effects = _make_private_chat_mocks(
        current_user_id=current_user_id,
        other_user_id=str(uuid4()),
        other_user_exists=False,
        last_msg_content=None,
        total_count=0,
    )
    mock_db.execute.side_effect = side_effects

    result = await _build_chat_response(chat, current_user_id, mock_db)

    # Имя должно быть дефолтным, а не падать с ошибкой
    assert result.name in ("Unknown", "Chat", "")


@pytest.mark.asyncio
async def test_build_chat_response_private_with_avatar():
    """Приватный чат — аватар собеседника пробрасывается в ответ"""
    mock_db = AsyncMock()
    current_user_id = str(uuid4())
    other_user_id = str(uuid4())
    avatar = "https://cdn.example.com/avatar.png"

    chat, side_effects = _make_private_chat_mocks(
        current_user_id=current_user_id,
        other_user_id=other_user_id,
        avatar_url=avatar,
        last_msg_content="Hi",
        total_count=1,
    )
    mock_db.execute.side_effect = side_effects

    result = await _build_chat_response(chat, current_user_id, mock_db)

    assert result.avatar_url == avatar


@pytest.mark.asyncio
async def test_build_chat_response_private_with_read_messages():
    """
    Если last_read_message_id установлен — unread считается только
    по сообщениям ПОСЛЕ него, а не total count.
    """
    mock_db = AsyncMock()
    current_user_id = str(uuid4())
    other_user_id = str(uuid4())

    chat = MagicMock(spec=Chat)
    chat.id = str(uuid4())
    chat.type = "private"

    # 1. Участники
    participants_result = MagicMock()
    participants_result.scalars.return_value.all.return_value = [current_user_id, other_user_id]

    # 2. Другой пользователь
    mock_user = MagicMock(spec=User)
    mock_user.username = "otheruser"
    mock_user.avatar_url = None
    user_result = MagicMock()
    user_result.scalar_one_or_none.return_value = mock_user

    # 3. Последнее сообщение
    last_msg = MagicMock(spec=Message)
    last_msg.content = "Latest"
    last_msg.created_at = None
    last_msg_result = MagicMock()
    last_msg_result.scalar_one_or_none.return_value = last_msg

    # 4. Участник с установленным last_read_message_id
    part = MagicMock()
    part.last_read_message_id = "some-message-id"  # прочитал до этого
    part_result = MagicMock()
    part_result.scalar_one_or_none.return_value = part

    # 5. Непрочитанных — только 2 (после last_read_message_id)
    unread_count_result = MagicMock()
    unread_count_result.scalar_one.return_value = 2

    mock_db.execute.side_effect = [
        participants_result,
        user_result,
        last_msg_result,
        part_result,
        unread_count_result,
    ]

    result = await _build_chat_response(chat, current_user_id, mock_db)

    assert result.unread_count == 2
    assert result.last_message == "Latest"


# ===========================================================================
# ГРУППОВОЙ ЧАТ
# ===========================================================================

@pytest.mark.asyncio
async def test_build_chat_response_group():
    """Групповой чат — имя берётся из chat.name, аватар None"""
    mock_db = AsyncMock()
    current_user_id = str(uuid4())

    chat = MagicMock(spec=Chat)
    chat.id = str(uuid4())
    chat.type = "group"
    chat.name = "Team Chat"

    # Групповой чат не делает запросы на участников/пользователя
    # Порядок: last_msg, participant, count
    last_msg = MagicMock(spec=Message)
    last_msg.content = "Welcome!"
    last_msg.created_at = None
    last_msg_result = MagicMock()
    last_msg_result.scalar_one_or_none.return_value = last_msg

    part = MagicMock()
    part.last_read_message_id = None
    part_result = MagicMock()
    part_result.scalar_one_or_none.return_value = part

    count_result = MagicMock()
    count_result.scalar_one.return_value = 10

    mock_db.execute.side_effect = [last_msg_result, part_result, count_result]

    result = await _build_chat_response(chat, current_user_id, mock_db)

    assert result.name == "Team Chat"
    assert result.avatar_url is None
    assert result.unread_count == 10
    assert result.last_message == "Welcome!"
    assert result.type == "group"


@pytest.mark.asyncio
async def test_build_chat_response_group_no_messages():
    """Групповой чат без сообщений"""
    mock_db = AsyncMock()
    current_user_id = str(uuid4())

    chat = MagicMock(spec=Chat)
    chat.id = str(uuid4())
    chat.type = "group"
    chat.name = "Empty Group"

    last_msg_result = MagicMock()
    last_msg_result.scalar_one_or_none.return_value = None

    part = MagicMock()
    part.last_read_message_id = None
    part_result = MagicMock()
    part_result.scalar_one_or_none.return_value = part

    count_result = MagicMock()
    count_result.scalar_one.return_value = 0

    mock_db.execute.side_effect = [last_msg_result, part_result, count_result]

    result = await _build_chat_response(chat, current_user_id, mock_db)

    assert result.last_message is None
    assert result.unread_count == 0
    assert result.name == "Empty Group"
