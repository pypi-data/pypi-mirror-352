import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
from imblearn.over_sampling import SMOTE
from tqdm import tqdm

class DSTO_GAN:
    """Data Sampling Technique Optimization with Generative Adversarial Networks
    
    A hybrid approach combining SMOTE and GANs for imbalanced dataset resampling.
    
    Parameters:
    -----------
    n_features : int
        Number of input features
    latent_dim : int, default=32
        Dimension of the latent space
    hidden_dim : int, default=128
        Dimension of hidden layers
    lr : float, default=0.0001
        Learning rate for optimizers
    batch_size : int, default=128
        Batch size for training
    n_critic : int, default=5
        Number of discriminator updates per generator update
    device : str, optional
        Device to use for training ('cuda' or 'cpu'). Auto-detected if None.
    """
    
    def __init__(self, n_features, latent_dim=32, hidden_dim=128, lr=0.0001, 
                 batch_size=128, n_critic=5, device=None):
        self.n_features = n_features
        self.latent_dim = latent_dim
        self.hidden_dim = hidden_dim
        self.lr = lr
        self.batch_size = batch_size
        self.n_critic = n_critic
        self.device = device or torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Initialize models
        self.encoder = self._build_encoder()
        self.decoder = self._build_decoder()
        self.discriminator = self._build_discriminator()
        
        # Optimizers
        self.optimizer_g = optim.Adam(
            list(self.encoder.parameters()) + list(self.decoder.parameters()),
            lr=lr, betas=(0.5, 0.999)
        )
        self.optimizer_d = optim.Adam(
            self.discriminator.parameters(),
            lr=lr, betas=(0.5, 0.999)
        
        # Loss functions
        self.criterion = nn.BCELoss()
        self.mse_loss = nn.MSELoss()
    
    def _build_encoder(self):
        """Build the encoder network"""
        return nn.Sequential(
            nn.Linear(self.n_features, self.hidden_dim),
            nn.BatchNorm1d(self.hidden_dim),
            nn.LeakyReLU(0.2),
            nn.Linear(self.hidden_dim, self.hidden_dim),
            nn.BatchNorm1d(self.hidden_dim),
            nn.LeakyReLU(0.2),
            nn.Linear(self.hidden_dim, self.latent_dim * 2)  # Outputs mean and logvar
        ).to(self.device)
    
    def _build_decoder(self):
        """Build the decoder/generator network"""
        return nn.Sequential(
            nn.Linear(self.latent_dim, self.hidden_dim),
            nn.BatchNorm1d(self.hidden_dim),
            nn.LeakyReLU(0.2),
            nn.Linear(self.hidden_dim, self.hidden_dim),
            nn.BatchNorm1d(self.hidden_dim),
            nn.LeakyReLU(0.2),
            nn.Linear(self.hidden_dim, self.n_features),
            nn.Tanh()
        ).to(self.device)
    
    def _build_discriminator(self):
        """Build the discriminator network"""
        return nn.Sequential(
            nn.Linear(self.n_features, 256),
            nn.LeakyReLU(0.2),
            nn.Linear(256, 256),
            nn.LeakyReLU(0.2),
            nn.Linear(256, 128),
            nn.LeakyReLU(0.2),
            nn.Linear(128, 1),
            nn.Sigmoid()
        ).to(self.device)
    
    def fit(self, X, y, epochs=200):
        """Train the DSTO-GAN model
        
        Parameters:
        -----------
        X : array-like of shape (n_samples, n_features)
            Training data
        y : array-like of shape (n_samples,)
            Target values (used for class balancing)
        epochs : int, default=200
            Number of training epochs
        """
        X_tensor = torch.FloatTensor(X).to(self.device)
        dataset = TensorDataset(X_tensor)
        dataloader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True)
        
        for epoch in tqdm(range(epochs), desc="Training DSTO-GAN"):
            for i, (real_samples,) in enumerate(dataloader):
                batch_size = real_samples.size(0)
                
                # Train Discriminator
                self.optimizer_d.zero_grad()
                
                # Real samples
                real_labels = torch.ones(batch_size, 1).to(self.device)
                outputs_real = self.discriminator(real_samples)
                d_loss_real = self.criterion(outputs_real, real_labels)
                
                # Fake samples
                z = torch.randn(batch_size, self.latent_dim).to(self.device)
                fake_samples = self.decoder(z)
                fake_labels = torch.zeros(batch_size, 1).to(self.device)
                outputs_fake = self.discriminator(fake_samples.detach())
                d_loss_fake = self.criterion(outputs_fake, fake_labels)
                
                # Total discriminator loss
                d_loss = d_loss_real + d_loss_fake
                d_loss.backward()
                self.optimizer_d.step()
                
                # Train Generator (every n_critic steps)
                if i % self.n_critic == 0:
                    self.optimizer_g.zero_grad()
                    
                    # Generate samples
                    z = torch.randn(batch_size, self.latent_dim).to(self.device)
                    generated_samples = self.decoder(z)
                    
                    # Generator loss
                    outputs = self.discriminator(generated_samples)
                    g_loss = self.criterion(outputs, real_labels)
                    
                    # Reconstruction loss
                    encoded = self.encoder(real_samples)
                    mean, logvar = encoded[:, :self.latent_dim], encoded[:, self.latent_dim:]
                    std = torch.exp(0.5 * logvar)
                    eps = torch.randn_like(std)
                    z_sample = mean + eps * std
                    reconstructed = self.decoder(z_sample)
                    reconstruction_loss = self.mse_loss(reconstructed, real_samples)
                    
                    # Total generator loss
                    total_g_loss = g_loss + reconstruction_loss
                    total_g_loss.backward()
                    self.optimizer_g.step()
    
    def resample(self, X, y):
        """Resample the dataset to balance classes using hybrid SMOTE-GAN approach
        
        Parameters:
        -----------
        X : array-like of shape (n_samples, n_features)
            Input data
        y : array-like of shape (n_samples,)
            Target labels
            
        Returns:
        --------
        tuple of (numpy.ndarray, numpy.ndarray)
            Resampled balanced dataset (X_resampled, y_resampled)
        """
        class_counts = np.bincount(y)
        major_count = np.max(class_counts)
        n_to_sample = {cls: major_count - cnt for cls, cnt in enumerate(class_counts) if cnt < major_count}
        
        synthetic_samples = []
        synthetic_labels = []
        
        for class_label, n_samples in n_to_sample.items():
            if n_samples > 0:
                # SMOTE samples
                smote = SMOTE(sampling_strategy={class_label: n_samples}, k_neighbors=5)
                X_smote, y_smote = smote.fit_resample(X, y)
                smote_samples = X_smote[-n_samples:]
                
                # GAN samples
                n_gan_samples = min(n_samples, 1000)
                z = torch.randn(n_gan_samples, self.latent_dim).to(self.device)
                gan_samples = self.decoder(z).cpu().detach().numpy()
                
                # Combine both
                combined_samples = np.vstack([smote_samples, gan_samples])[:n_samples]
                synthetic_samples.append(combined_samples)
                synthetic_labels.append(np.array([class_label] * n_samples))
        
        if synthetic_samples:
            X_resampled = np.vstack([X] + synthetic_samples)
            y_resampled = np.concatenate([y] + synthetic_labels)
            return X_resampled, y_resampled
        return X, y

def calculate_class_weights(y):
    """Calculate class weights for imbalanced datasets
    
    Parameters:
    -----------
    y : array-like of shape (n_samples,)
        Target labels
        
    Returns:
    --------
    dict
        Dictionary of class weights {class: weight}
    """
    class_counts = np.bincount(y)
    total = np.sum(class_counts)
    return {cls: total / (len(class_counts) * cnt) for cls, cnt in enumerate(class_counts)}