# import os
# import django
# import logging
# from django.db.models import Q

# logging.basicConfig(level=logging.DEBUG)

# # DJANGO_SETTINGS_MODULE 환경 변수를 설정
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Renaissance.settings")

# # Django 설정을 로드
# django.setup()
# logging.debug("Django settings loaded successfully.")

# # 캐시 폴더 설정 및 생성
# cache_folder = '.embading/models'
# if not os.path.exists(cache_folder):
#     os.makedirs(cache_folder)
# logging.debug(f"Cache folder set to {cache_folder}")

# # 임베딩 모델 로드 (캐시된 모델 사용)
# try:
#     from sentence_transformers import SentenceTransformer
#     model = SentenceTransformer('snunlp/KR-SBERT-V40K-klueNLI-augSTS', cache_folder=cache_folder)
#     logging.debug("Embedding model loaded successfully.")
# except Exception as e:
#     logging.error(f"Error loading embedding model: {e}")

# # 모델 임포트
# try:
#     from articleapp.models import Article
#     logging.debug("Article model imported successfully.")
# except Exception as e:
#     logging.error(f"Error importing Article model: {e}")

# def generate_and_save_embeddings():
#     articles = Article.objects.filter(
#         Q(title_embedding__isnull=True) | 
#         Q(content_embedding__isnull=True) | 
#         Q(combined_text_embedding__isnull=True)
#     )
#     total_articles = articles.count()
#     logging.debug(f"Total articles to process: {total_articles}")

#     for index, article in enumerate(articles, start=1):
#         title_embedding = model.encode(article.title).tobytes()
#         content_embedding = model.encode(article.content).tobytes()
#         combined_text = article.get_combined_text()
#         combined_text_embedding = model.encode(combined_text).tobytes()
        
#         article.title_embedding = title_embedding
#         article.content_embedding = content_embedding
#         article.combined_text_embedding = combined_text_embedding
#         article.save()
#         logging.info(f"임베딩 생성 및 저장 완료: {article.id} - {article.title} ({index}/{total_articles})")

# if __name__ == '__main__':
#     generate_and_save_embeddings()
#     logging.info("모든 Article의 임베딩 생성 및 저장이 완료되었습니다.")
