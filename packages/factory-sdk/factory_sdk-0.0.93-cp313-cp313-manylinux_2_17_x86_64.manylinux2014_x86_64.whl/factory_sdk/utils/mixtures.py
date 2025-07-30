from tqdm.auto import tqdm
from sklearn.mixture import GaussianMixture
import numpy as np
from factory_sdk.dto.model import ModelChatInput
from factory_sdk.dto.dataset import DatasetDistributionMixture


def compute_embeddings(
    data,
    reloaded_fn,
    embedding_text_model,
    embedding_img_model,
    EMBEDDING_SAMPLE_LIMIT,
    TEXT_SEQUENCE_LENGTH,
    TEXT_STRIDE_LENGTH,
):
    img_embeddings = []
    text_embeddings = []

    if len(data) > EMBEDDING_SAMPLE_LIMIT:
        d = data.train_test_split(
            test_size=EMBEDDING_SAMPLE_LIMIT, shuffle=True, seed=42
        )["test"]
    else:
        d = data
    for i in tqdm(range(len(d)), desc="Compute embeddings..."):
        row = d[i]
        x: ModelChatInput = reloaded_fn(row)
        texts = []
        images = []
        for m in x.messages:
            t = m.content
            if len(t) > TEXT_SEQUENCE_LENGTH:
                for i in range(0, len(t), TEXT_STRIDE_LENGTH):
                    texts.append(t[i : i + TEXT_STRIDE_LENGTH])
            else:
                texts.append(t)
        for img in x.images:
            images.append(img)

        if len(texts) > 0:
            z_text = embedding_text_model.encode(texts, show_progress_bar=False)
            text_embeddings.append(z_text)
        if len(images) > 0:
            z_img = embedding_img_model.encode(images, show_progress_bar=False)
            img_embeddings.append(z_img)

    # Assuming embeddings is your numpy array of embedding vectors
    text_embeddings = np.vstack(text_embeddings)
    img_embeddings = np.vstack(img_embeddings) if len(img_embeddings) > 0 else None

    return text_embeddings, img_embeddings


def predict_samples(
    text_gmm,
    img_gmm,
    data,
    reloaded_fn,
    embedding_text_model,
    embedding_img_model,
    EMBEDDING_SAMPLE_LIMIT,
    TEXT_SEQUENCE_LENGTH,
    TEXT_STRIDE_LENGTH,
):
    text_embeddings, img_embeddings = compute_embeddings(
        data,
        reloaded_fn,
        embedding_text_model,
        embedding_img_model,
        EMBEDDING_SAMPLE_LIMIT,
        TEXT_SEQUENCE_LENGTH,
        TEXT_STRIDE_LENGTH,
    )
    text_scores = text_gmm.score_samples(text_embeddings)
    img_scores = (
        img_gmm.score_samples(img_embeddings) if img_embeddings is not None else None
    )

    return text_scores, img_scores


def reconstruct_mixture(gmm_params: DatasetDistributionMixture):
    gmm = GaussianMixture(
        n_components=len(gmm_params.weights), covariance_type=gmm_params.covariance_type
    )
    gmm.weights_ = np.array(gmm_params.weights)
    gmm.means_ = np.array(gmm_params.means)
    gmm.covariances_ = np.array(gmm_params.covariances)
    gmm.precisions_ = np.array(gmm_params.precisions)
    gmm.precisions_cholesky_ = np.array(gmm_params.precisions_cholesky)

    return gmm


def find_optimal_components(embeddings, max_components=16, embedding_type="text"):
    n_components_range = range(1, max_components + 1)
    bic = []
    gmms = []

    print(
        f"Finding optimal number of components for representing the {embedding_type} dataset distribution..."
    )
    for n_components in tqdm(n_components_range):
        gmm = GaussianMixture(n_components=n_components, random_state=42)
        gmm.fit(embeddings)
        bic.append(gmm.bic(embeddings))
        gmms.append(gmm)

    optimal_n_bic = n_components_range[np.argmin(bic)]
    optimal_gmm = gmms[np.argmin(bic)]

    return optimal_n_bic, bic, optimal_gmm


def compute_mixtures(
    data,
    reloaded_fn,
    embedding_text_model,
    embedding_img_model,
    EMBEDDING_SAMPLE_LIMIT,
    TEXT_SEQUENCE_LENGTH,
    TEXT_STRIDE_LENGTH,
):
    train_gmm_text_params = None
    train_gmm_img_params = None

    text_embeddings, img_embeddings = compute_embeddings(
        data,
        reloaded_fn,
        embedding_text_model,
        embedding_img_model,
        EMBEDDING_SAMPLE_LIMIT,
        TEXT_SEQUENCE_LENGTH,
        TEXT_STRIDE_LENGTH,
    )

    optimal_n_bic, bic, gmm = find_optimal_components(text_embeddings, 16, "text")

    print(f"Optimal number of components for text embeddings: {optimal_n_bic}")

    gmm_params = {
        "covariance_type": gmm.covariance_type,
        "weights": gmm.weights_,
        "means": gmm.means_,
        "covariances": gmm.covariances_,
        "precisions": gmm.precisions_,
        "precisions_cholesky": gmm.precisions_cholesky_,
    }

    train_gmm_text_params = gmm_params

    if img_embeddings is not None and len(img_embeddings) > 0:
        img_embeddings = np.vstack(img_embeddings)

        optimal_n_bic, bic, gmm = find_optimal_components(img_embeddings, 16, "image")

        print(f"Optimal number of components for image embeddings: {optimal_n_bic}")

        gmm_params = {
            "covariance_type": gmm.covariance_type,
            "weights": gmm.weights_,
            "means": gmm.means_,
            "covariances": gmm.covariances_,
            "precisions": gmm.precisions_,
            "precisions_cholesky": gmm.precisions_cholesky_,
        }

        train_gmm_img_params = gmm_params

    train_gmm_text_params = DatasetDistributionMixture(
        covariance_type=train_gmm_text_params["covariance_type"],
        weights=train_gmm_text_params["weights"].tolist(),
        means=train_gmm_text_params["means"].tolist(),
        covariances=train_gmm_text_params["covariances"].tolist(),
        precisions=train_gmm_text_params["precisions"].tolist(),
        precisions_cholesky=train_gmm_text_params["precisions_cholesky"].tolist(),
    )

    if train_gmm_img_params:
        train_gmm_img_params = DatasetDistributionMixture(
            covariance_type=train_gmm_img_params["covariance_type"],
            weights=train_gmm_img_params["weights"].tolist(),
            means=train_gmm_img_params["means"].tolist(),
            covariances=train_gmm_img_params["covariances"].tolist(),
            precisions=train_gmm_img_params["precisions"].tolist(),
            precisions_cholesky=train_gmm_img_params["precisions_cholesky"].tolist(),
        )

    return train_gmm_text_params, train_gmm_img_params
