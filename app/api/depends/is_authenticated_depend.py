from fastapi import Request, HTTPException

# Logs Import
from logger_config import log_writer, log_rename

# DAOS Import
# from app.daos.route_dao import nt_route_DAO
# route_dao = nt_route_DAO()

# Utils Import
from app.utils.token_manager import decode as token_decoder


async def verify_authentication(request: Request):
    log_file = request.state.log_file
    authorization = request.headers.get('authorization')
    if authorization:
        decoded_token = await token_decoder(str(authorization.split(" ")[1]))  # Passing token
        log_writer(log_file, f"VERIFY AUTHENTICATION - Result of decoded token {decoded_token}")
        if 'id_account' in decoded_token:
            request.state.log_file = log_rename(log_file, decoded_token['id_account'])
            request.state.requester = {"authenticated": True, "decoded_token": decoded_token}
            return {
                "authenticated": True,
                "decoded_token": decoded_token               
            }
    raise HTTPException(status_code=401, detail="Unauthorized - Token not provided")

# CAUTION: Used in case you want to control the permissions via database (using tables and registries)
# async def verify_authorization(request: Request):
#     log_file = request.state.log_file
#     requester = request.state.requester
#     destination = request.__dict__['scope']['route'].path
#     destination = destination[:-1] if destination[-1] == "/" else destination
#     method = request.__dict__['scope']['method'].lower()
#     log_writer(log_file, f"Depend - Request to endpoint: {destination}. Method: {method}")
#     destination_needed_permissions = await route_dao.select_route_permissions(destination, method, log_file)
#     if destination_needed_permissions:
#         for permission in destination_needed_permissions:
#             permission = dict(permission)
#             if permission['title'] not in requester['decoded_token']['permissions']:
#                 raise HTTPException(status_code=403, detail="Unauthorized - Permission Denied!")
#     return True    
    