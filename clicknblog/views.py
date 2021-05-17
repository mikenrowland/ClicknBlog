from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
from django.urls import reverse_lazy
from .models import Post
from django import forms
from .forms import NewUserForm, CommentForm
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes


# Create your views here.
class HomePageView(TemplateView):
	template_name = 'home.html'

class BlogListView(ListView):
    model = Post
    template_name = 'post_list.html'

class BlogCreateView(LoginRequiredMixin, CreateView):
	model = Post
	template_name = 'post_new.html'
	fields = ('title', 'body',)
	def form_valid(self, form):
		form.instance.author = self.request.user
		return super().form_valid(form)

class BlogUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
	model = Post
	fields = ('title', 'body',)
	template_name = 'post_edit.html'
	def test_func(self):
		obj = self.get_object()
		return obj.author == self.request.user

class BlogDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
	model = Post
	template_name = 'post_delete.html'
	success_url = reverse_lazy('post_list')
	def test_func(self):
		obj = self.get_object()
		return obj.author == self.request.user


def register_request(request):
	logout(request)
	if request.method == "POST":
		form = NewUserForm(request.POST)
		if form.is_valid():
			user = form.save()
			#login(request, user)
			messages.success(request, "Registration successful." )
			return redirect("login")
		else:
			messages.error(request, "Unsuccessful registration. Invalid information.")
	else:
		form = NewUserForm
	return render (request=request, template_name="reg.html", context={"register_form":form})

def login_request(request):
	logout(request)
	if request.method == "POST":
		form = AuthenticationForm(request, data=request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				messages.info(request, f"You are now logged in as {username}.")
				return redirect("home")
			else:
				messages.error(request,"Invalid username or password.")
		else:
			messages.error(request,"Invalid username or password.")
	else:
		form = AuthenticationForm()
	return render(request=request, template_name="login.html", context={"login_form":form})

def logout_request(request):
    logout(request)
    messages.info(request, "You have successfully logged out.") 
    return redirect("login")

def password_reset_request(request):
	if request.method == "POST":
		password_reset_form = PasswordResetForm(request.POST)
		if password_reset_form.is_valid():
			data = password_reset_form.cleaned_data['email']
			associated_users = User.objects.filter(Q(email=data))
			if associated_users.exists():
				for user in associated_users:
					subject = "Password Reset Requested"
					email_template_name = "password/password_reset_email.txt"
					c = {
					"email":user.email,
					'domain':'clicknblog.herokuapp.com',
					'site_name': 'clicknblog',
					"uid": urlsafe_base64_encode(force_bytes(user.pk)),
					"user": user,
					'token': default_token_generator.make_token(user),
					'protocol': 'https',
					}
					email = render_to_string(email_template_name, c)
					try:
						send_mail(subject, email, 'myclicknblog@gmail.com' , [user.email], fail_silently=False)
					except BadHeaderError:
						return HttpResponse('Invalid header found.')
					return redirect ("/password_reset/done/")
	password_reset_form = PasswordResetForm()
	return render(request=request, template_name="password/password_reset.html", context={"password_reset_form":password_reset_form})

def post_detail(request, pk):
	post = get_object_or_404(Post, pk=pk)
	
	if request.method == 'POST':
		form = CommentForm(request.POST)
		if form.is_valid():
			comment = form.save(commit=False)
			comment.post = post
			comment.author = request.user
			comment.save()
			return redirect('post_detail', pk=pk)
	else:
		form = CommentForm()

	return render(request, 'post_detail.html', {'post': post,'form': form})
