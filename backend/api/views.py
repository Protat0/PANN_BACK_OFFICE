from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def pos_status(request):
    return Response({
        'message': 'POS System API is running!',
        'status': 'active',
        'version': '1.0.0'
    })