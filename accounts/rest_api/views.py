from django.contrib.auth import login
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from knox.views import LoginView as KnoxLoginView

from accounts.models import User, EmailActivation
from ml.text_detection import confirm_name
from ml.face_same import recognize_face
from ml.htr.address_detection import recognize_addr
from .serializers import IdImageSerializer, WalletImageSerializer, \
    FinalSaveToDbSerializer, LoginSerializer, ReactivateEmailSerializer, SignupSerializer
from web3op.id_db import set_verified_on_bc


# Auth Views
class LoginView(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return super(LoginView, self).post(request, format=None)


class UserCreateView(CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    queryset = User.objects.all()
    serializer_class = SignupSerializer

    def post(self, request, *args, **kwargs):
        return super(UserCreateView, self).post(request, *args, **kwargs)


class AccountsEmailActivation(APIView):
    def get(self, request, key=None, *args, **kwargs):
        self.key = key
        if key is not None:
            qs = EmailActivation.objects.filter(key__iexact=key)
            confirm_qs = qs.confirmable()
            if confirm_qs.count() == 1:
                obj = confirm_qs.first()
                obj.activate()
                return Response({"message": "Your account has been activated!", "activated": True}, status=status.HTTP_200_OK)
            else:
                activated_qs = qs.filter(activated=True)
                if activated_qs.exists():
                    message = "Your email has already been activated. Do you want to reset your password ?"
                    return Response({"message": message, "activated": True}, status=status.HTTP_200_OK)
                return Response({"message": "Your Verification Link has expired! Please Regenerate the link!"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Key cannot be none! Recheck the link."}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        serializer = ReactivateEmailSerializer(request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data.get("email")
            email_act_obj = EmailActivation.objects.email_exists(email).first()
            user = email_act_obj.user
            new_obj = EmailActivation.objects.create(email=email, user=user)
            new_obj.send_activation()
            return Response({"message": "New Activation Link Sent! Check Your Inbox."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Verify Views
class PostIdImageView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = IdImageSerializer(instance=request.user, data=request.data)
        if serializer.is_valid():
            name_is_valid = confirm_name(serializer.validated_data['id_image'], request.user.full_name)
            if name_is_valid:
                serializer.validated_data['name_check'] = True
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'id_image': "Name does not match in Id!"}, status=status.HTTP_400_BAD_REQUEST)


class PostWalletImageView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = WalletImageSerializer(instance=request.user, data=request.data)
        if serializer.is_valid():
            wallet_face_image = serializer.validated_data['waddr_image']
            face_is_valid = recognize_face(request.user.id_image, wallet_face_image)
            address_is_valid = recognize_addr(serializer.validated_data["eth_name"], wallet_face_image)
            if face_is_valid:
                serializer.validated_data['face_check'] = True
            else:
                return Response({'message': "Face does not match your Id!"}, status=status.HTTP_400_BAD_REQUEST)
            if address_is_valid:
                serializer.validated_data['waddr_check'] = True
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({'message': "Wallet address does not match the photo"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': "Invalid data!"}, status=status.HTTP_400_BAD_REQUEST)


class FinalSavePostView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        final_db_save = FinalSaveToDbSerializer(data=request.data)
        if final_db_save.is_valid():
            validated_data = final_db_save.validated_data
            ens = validated_data.get("ens", None)
            user = request.user
            if not user.is_active:
                return Response({'user': "User not active!"}, status=status.HTTP_400_BAD_REQUEST)
            if not user.is_verified:
                if not user.face_check:
                    return Response({'user': "Please verify your Id and Face first!"}, status=status.HTTP_400_BAD_REQUEST)
                if not user.name_check:
                    return Response({'user': "Please verify your name first using Id!"}, status=status.HTTP_400_BAD_REQUEST)
                if not user.waddr_check:
                    return Response({'user': "Please verify wallet address first!"}, status=status.HTTP_400_BAD_REQUEST)
                set_verified_on_bc(ens, user.full_name)
                validated_data['is_verified'] = True
                user.is_verified = True
                user.save()
                return Response(final_db_save.data, status=status.HTTP_200_OK)
            return Response({'user': "User already verified!"}, status=status.HTTP_400_BAD_REQUEST)
