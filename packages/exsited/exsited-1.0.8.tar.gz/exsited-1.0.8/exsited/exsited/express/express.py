from exsited.exsited.express.dto.express_dto import ExpressDTO
from exsited.exsited.express.express_api_url import ExpressApiUrl
from exsited.exsited.order.dto.order_dto import OrderDetailsDTO
from exsited.http.ab_rest_processor import ABRestProcessor


class Express(ABRestProcessor):

    def create(self, request_data: ExpressDTO) -> OrderDetailsDTO:
        response = self.post(url=ExpressApiUrl.EXPRESS_CREATE, request_obj=request_data, response_obj=OrderDetailsDTO())
        return response
