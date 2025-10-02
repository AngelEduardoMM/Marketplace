from django.views import View
from django.views.generic import ListView, TemplateView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.core.cache import cache
from django.urls import reverse_lazy
from .models import Product, Category, Message
from .forms import MessageForm, ProductForm

class HomeView(TemplateView):
    template_name = 'marketplace/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Cache categories for better performance
        categories = cache.get('categories')
        if not categories:
            categories = Category.objects.all()
            cache.set('categories', categories, 300)  # 5 minutes
        
        context['categories'] = categories
        context['featured_products'] = Product.objects.filter(
            status='available'
        ).select_related('category').order_by('-created_at')[:8]
        return context

class ProductListView(ListView):
    model = Product
    template_name = 'marketplace/list.html'
    context_object_name = 'products'
    paginate_by = 12
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = Product.objects.filter(status='available').select_related('category')
        
        # Search functionality
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        # Category filter
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Condition filter
        condition = self.request.GET.get('condition')
        if condition:
            queryset = queryset.filter(condition=condition)
        
        # Price filter
        max_price = self.request.GET.get('max_price')
        if max_price:
            try:
                queryset = queryset.filter(price__lte=float(max_price))
            except ValueError:
                pass
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = cache.get('categories')
        if not categories:
            categories = Category.objects.all()
            cache.set('categories', categories, 300)
        context['categories'] = categories
        return context

class ProductDetailView(View):
    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        product.increment_views()
        
        # Get related products
        related_products = Product.objects.filter(
            category=product.category,
            status='available'
        ).exclude(id=product.id).select_related('category')[:4]
        
        form = MessageForm()
        return render(request, 'marketplace/product_detail.html', {
            'product': product,
            'related_products': related_products,
            'form': form,
        })
    
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        
        if not request.user.is_authenticated:
            messages.error(request, 'Debes iniciar sesión para enviar mensajes')
            return redirect('/usuarios/accounts/login/')
        
        if request.user == product.seller:
            messages.error(request, 'No puedes enviarte mensajes a ti mismo')
            return redirect('marketplace:product_detail', product_id=product.id)
        
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.product = product
            message.sender = request.user
            message.receiver = product.seller
            message.save()
            messages.success(request, 'Mensaje enviado correctamente')
            return redirect('marketplace:product_detail', product_id=product.id)
        
        related_products = Product.objects.filter(
            category=product.category,
            status='available'
        ).exclude(id=product.id).select_related('category')[:4]
        
        return render(request, 'marketplace/product_detail.html', {
            'product': product,
            'related_products': related_products,
            'form': form,
        })

class VistaPrivada(LoginRequiredMixin, TemplateView):
    template_name = 'marketplace/privado.html'

class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'marketplace/product_form.html'
    success_url = reverse_lazy('marketplace:product_list')

    def form_valid(self, form):
        form.instance.seller = self.request.user
        return super().form_valid(form)

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'marketplace/product_form.html'
    success_url = reverse_lazy('marketplace:product_list')

    def get_queryset(self):
        return Product.objects.filter(seller=self.request.user)

class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'marketplace/product_confirm_delete.html'
    success_url = reverse_lazy('marketplace:product_list')

    def get_queryset(self):
        return Product.objects.filter(seller=self.request.user)