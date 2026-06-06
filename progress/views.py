from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from progress.runner import run_koan_tests

class ProgressView(APIView):
    """
    GET /api/progress/
    Runs the compliance unit tests and returns the overall progress stats.
    """
    def get(self, request, *args, **kwargs):
        try:
            stats = run_koan_tests()
            return Response(stats, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Failed to run koans test runner: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
