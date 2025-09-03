import pytest
import asyncio

from app.services.client_users import ClientUsers, ClientUserPost, QueryFilters
from app.services.clients import Clients
from app.services.users import Users    
from app.drivers.db import async_session
from sqlalchemy import text


class TestClientUsersIntegration:
    @pytest.mark.asyncio
    async def test_save_or_update_new_user_new_client_user(self):
        """Test creating a new user and client user relationship"""
        # Create test data
        

        # user = await Users().create("Test User","test_user@example.com","test_password")
        # print(user)


        # client = await Clients().create("Test Client",user.id)
        # print(client)

        client_users_service = ClientUsers()

        client_user_post = ClientUserPost(
            email="test_integration_new@example.com",
            name="Integration Test User",
            avatar="test_avatar.jpg",
            client_id="rmwujXdn6KzuKxhPufYG"

        )
        
        # Execute the service method
        result_id = await client_users_service.save_or_update(client_user_post)
        
        # Verify the result
        assert result_id is not None
        print(result_id)
        
        # Verify user was created in database

    @pytest.mark.asyncio
    async def test_get_user_info(self):
        """Test querying client users"""
        user_info = await ClientUsers().get_user_info("rEKYnPa6P7I2Sn7i5pd8", "rmwujXdn6KzuKxhPufYG")
        print(user_info)