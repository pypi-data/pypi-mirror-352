import uuid
import requests
import time
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseBadRequest
from .utils.decorators import aluno_login_required
from .utils.sso import get_valid_access_token
from wagtail.models import Page

from django.shortcuts import render

def teste_login_sso(request):
	return render(request, "teste_login_sso.html")

def login_sso(request):
	redirect_uri = request.build_absolute_uri(settings.SSO_REDIRECT_PATH)

	# Gera state único para segurança (proteção CSRF)
	state = str(uuid.uuid4())

	# print("Redirect URI gerado:", redirect_uri)
	# Monta query com todos os parâmetros
	query = {
		"client_id": settings.SSO_CLIENT_ID,
		"redirect_uri": redirect_uri,
		"response_type": "code",
		"scope": "openid",
		"state": state,
	}

	# Monta URL final do SSO
	sso_login_url = f"{settings.SSO_AUTH_URL}?{'&'.join(f'{k}={v}' for k, v in query.items())}"
	return redirect(sso_login_url)

def callback_sso(request):
	code = request.GET.get("code")
	if not code:
		return HttpResponseBadRequest("Código de autorização ausente.")

	# 🛑 IMPORTANTE: esta URL precisa ser exatamente igual à registrada no Keycloak
	redirect_uri = request.build_absolute_uri(settings.SSO_REDIRECT_PATH)

	data = {
		"grant_type": "authorization_code",
		"code": code,
		"redirect_uri": redirect_uri,
		"client_id": settings.SSO_CLIENT_ID,
		"client_secret": settings.SSO_CLIENT_SECRET,
	}
	headers = {
		"Content-Type": "application/x-www-form-urlencoded"
	}

	# ⚠️ Desativa verificação SSL apenas em DEV
	verify_ssl = not settings.DEBUG

	# 🔐 Solicita o token
	print("📥 Enviando para /token:", data)
	token_response = requests.post(
		settings.SSO_TOKEN_URL,
		data=data,
		headers=headers,
		verify=verify_ssl
	)
	print("🧾 TOKEN RESPONSE:", token_response.status_code, token_response.text)

	if token_response.status_code != 200:
		return HttpResponse("Erro ao obter token", status=token_response.status_code)

	access_token = token_response.json().get("access_token")
	if not access_token:
		return HttpResponse("Token de acesso não recebido.", status=400)

	# 🔍 Pega dados do usuário
	userinfo_headers = {
		"Authorization": f"Bearer {access_token}"
	}
	user_info_response = requests.get(
		settings.SSO_USERINFO_URL,
		headers=userinfo_headers,
		verify=verify_ssl
	)

	if user_info_response.status_code != 200:
		return HttpResponse("Erro ao obter informações do usuário.", status=400)

	user_info = user_info_response.json()
	email = user_info.get("email")
	nome = user_info.get("name")
	cpf = user_info.get("cpf")
	print("user_info", user_info)
	if not email or not nome:
		return HttpResponse("Informações essenciais ausentes no SSO.", status=400)

	# 🧠 Armazena na sessão para uso em /area-do-aluno
	request.session["aluno_sso"] = {
		"email": email,
		"nome": nome,
		"cpf": cpf,
		"access_token": access_token,
		"refresh_token": token_response.json().get("refresh_token"),
		"access_token_expires_at": int(time.time()) + token_response.json().get("expires_in", 300),
	}

	return redirect(get_area_do_aluno_url())

def logout_view(request):
	request.session.flush()
	return render(request, "logout_intermediario.html")

def get_area_do_aluno_url():
	try:
		page = Page.objects.get(slug="area-do-aluno").specific
		return page.url
	except Page.DoesNotExist:
		return "/"
	
@aluno_login_required
def area_do_aluno(request):
	token = get_valid_access_token(request.session)
	if not token:
		return redirect("/")

	# Exemplo: usar o token para chamar API externa
	response = requests.get("https://api.enap.gov.br/aluno", headers={
		"Authorization": f"Bearer {token}"
	})
	aluno_dados = response.json()

	return render(request, "area_do_aluno.html", {
		"aluno": request.session["aluno_sso"],
		"dados": aluno_dados,
	})