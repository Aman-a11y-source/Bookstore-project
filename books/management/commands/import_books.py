# books/management/commands/import_books.py

import requests
from django.core.management.base import BaseCommand, CommandError
from books.models import Book, Authors # Corrected import for Authors model
from datetime import datetime
import traceback # For more detailed error logging

class Command(BaseCommand):
    help = 'Imports book data from Google Books API for specified queries or categories.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--query',
            type=str,
            help='A search query for books (e.g., "programming", "fiction", "history").',
            default='programming' # Default query if none provided
        )
        parser.add_argument(
            '--max_results',
            type=int,
            help='Maximum number of results to fetch per API call (max 40).',
            default=40
        )
        parser.add_argument(
            '--num_pages',
            type=int,
            help='Number of pages (API calls) to fetch for the query.',
            default=1 # Fetch 1 page (up to 40 results) by default
        )
        parser.add_argument(
            '--api_key',
            type=str,
            help='Your Google Books API Key (optional, but recommended for higher limits).',
            default='' # Leave empty if not using an API key
        )

    def handle(self, *args, **options):
        query = options['query']
        max_results = min(options['max_results'], 40) # Google Books API max results per call is 40
        num_pages = options['num_pages']
        api_key = options['api_key']

        self.stdout.write(self.style.SUCCESS(f'Starting import for query: "{query}"'))

        base_url = "https://www.googleapis.com/books/v1/volumes"
        
        total_imported = 0
        total_skipped = 0
        total_updated = 0

        for page in range(num_pages):
            params = {
                'q': query,
                'maxResults': max_results,
                'startIndex': page * max_results # For pagination
            }
            if api_key:
                params['key'] = api_key
            
            try:
                self.stdout.write(self.style.NOTICE(f'Fetching page {page + 1} (startIndex={page * max_results})...'))
                response = requests.get(base_url, params=params)
                response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
                data = response.json()

                if 'items' not in data or not data['items']:
                    self.stdout.write(self.style.WARNING(f'No more items found for query "{query}" on page {page + 1}. Stopping.'))
                    break

                for item in data['items']:
                    volume_info = item.get('volumeInfo', {})
                    
                    title = volume_info.get('title')
                    if not title: # Skip if no title
                        self.stdout.write(self.style.WARNING(f'Skipping item with no title: {item.get("id")}'))
                        total_skipped += 1
                        continue

                    # --- Extract Authors ---
                    authors_data = volume_info.get('authors', [])
                    book_authors_instances = []
                    for author_name in authors_data:
                        author_obj, created = Authors.objects.get_or_create(name=author_name)
                        book_authors_instances.append(author_obj)

                    # --- Extract ISBN ---
                    isbn_value = None
                    for identifier in volume_info.get('industryIdentifiers', []):
                        if identifier.get('type') == 'ISBN_13':
                            isbn_value = identifier.get('identifier')
                            break # Prefer ISBN_13
                        elif identifier.get('type') == 'ISBN_10' and not isbn_value:
                            isbn_value = identifier.get('identifier') # Fallback to ISBN_10 if 13 not found

                    # --- Extract Published Date ---
                    published_date_str = volume_info.get('publishedDate')
                    published_date_obj = None
                    if published_date_str:
                        try:
                            # Attempt to parse various date formats
                            if len(published_date_str) == 4: # YYYY (e.g., "2023")
                                published_date_obj = datetime.strptime(published_date_str, '%Y').date()
                            elif len(published_date_str) == 7 and published_date_str.count('-') == 1: # YYYY-MM (e.g., "2023-01")
                                published_date_obj = datetime.strptime(published_date_str, '%Y-%m').date()
                            else: # YYYY-MM-DD (e.g., "2023-01-15")
                                published_date_obj = datetime.strptime(published_date_str, '%Y-%m-%d').date()
                        except ValueError:
                            self.stdout.write(self.style.WARNING(f"Could not parse date: '{published_date_str}' for book '{title}'"))
                            pass # published_date_obj remains None

                    # --- Extract Descriptions ---
                    full_description = volume_info.get('description', '')
                    short_desc = full_description[:512] if full_description else '' # Truncate for shortDescription
                    long_desc = full_description # Use full for longDescription

                    # --- Extract Categories ---
                    categories_list = volume_info.get('categories', [])
                    categories_str = ", ".join(categories_list)[:256] # Join and truncate for CharField

                    # --- Prepare Book Data ---
                    book_data = {
                        'pageCount': volume_info.get('pageCount', 0),
                        'thumbnailUrl': volume_info.get('imageLinks', {}).get('thumbnail'),
                        'shortDescription': short_desc,
                        'longDescription': long_desc,
                        'isbn': isbn_value,
                        'publishedDate': published_date_obj,
                        'categories': categories_str,
                        'status': 'PUBLISH' # Default status
                    }

                    # --- Create or Update Book ---
                    try:
                        # Try to find by ISBN first if available and unique is set on model
                        # If ISBN is not unique, or null=True, you might still get duplicates.
                        # For now, using title for get_or_create as a primary key is not ideal.
                        # A better approach would be to add a `google_books_id` to your Book model.
                        
                        # Using title as the main identifier for get_or_create for now
                        book, created = Book.objects.get_or_create(
                            title=title,
                            defaults=book_data
                        )

                        if created:
                            book.authors.set(book_authors_instances) # Set authors for new books
                            self.stdout.write(self.style.SUCCESS(f'Successfully imported new book: "{title}"'))
                            total_imported += 1
                        else:
                            # If book already exists, update its fields (optional, depends on your needs)
                            updated_fields = []
                            for key, value in book_data.items():
                                current_value = getattr(book, key)
                                if current_value != value:
                                    setattr(book, key, value)
                                    updated_fields.append(key)
                            
                            # Check if authors need updating (only if the list of authors has changed)
                            current_authors_names = set(a.name for a in book.authors.all())
                            new_authors_names = set(a.name for a in book_authors_instances)
                            if current_authors_names != new_authors_names:
                                book.authors.set(book_authors_instances)
                                updated_fields.append('authors')

                            if updated_fields:
                                book.save()
                                self.stdout.write(self.style.WARNING(f'Updated existing book: "{title}" (Fields: {", ".join(updated_fields)})'))
                                total_updated += 1
                            else:
                                self.stdout.write(self.style.NOTICE(f'Skipped existing book: "{title}" (no changes)'))
                                total_skipped += 1

                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error processing book "{title}": {e}'))
                        self.stdout.write(self.style.ERROR(traceback.format_exc())) # Print full traceback
                        total_skipped += 1 # Count as skipped due to error

            except requests.exceptions.RequestException as e:
                self.stdout.write(self.style.ERROR(f'HTTP Error fetching data from Google Books API on page {page + 1}: {e}'))
                raise CommandError(f'API request failed. See error above.')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'An unexpected error occurred while processing page {page + 1}: {e}'))
                self.stdout.write(self.style.ERROR(traceback.format_exc())) # Print full traceback
                raise CommandError(f'Processing failed. See error above.')

        self.stdout.write(self.style.SUCCESS(f'Import complete. Total new books imported: {total_imported}, updated: {total_updated}, skipped/errors: {total_skipped}.'))

