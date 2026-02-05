from django.test import TestCase
from django.urls import reverse
from catalog.models import Series

class TrendingLogicTests(TestCase):
    def setUp(self):
        # Create 6 series
        self.series_list = []
        for i in range(6):
            series = Series.objects.create(
                title=f'Series {i}',
                description='Test description',
                views_count=10 * i # 0, 10, 20, 30, 40, 50
            )
            self.series_list.append(series)

    def test_trending_context(self):
        """Test that the catalog index contains 5 top viewed series in correct order"""
        response = self.client.get(reverse('catalog:index'))
        self.assertEqual(response.status_code, 200)
        
        trending = response.context['trending_series']
        self.assertEqual(len(trending), 5)
        
        # Check order (highest views first)
        self.assertEqual(trending[0], self.series_list[5]) # 50 vues
        self.assertEqual(trending[1], self.series_list[4]) # 40 vues
        self.assertEqual(trending[2], self.series_list[3]) # 30 vues
        self.assertEqual(trending[3], self.series_list[2]) # 20 vues
        self.assertEqual(trending[4], self.series_list[1]) # 10 vues
        
        # Ensure Series 0 (0 views) is not in top 5
        self.assertNotIn(self.series_list[0], trending)

    def test_view_increment(self):
        """Test that accessing detail view increments views_count"""
        series = self.series_list[0]
        initial_views = series.views_count
        
        url = reverse('catalog:detail', args=[series.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        series.refresh_from_db()
        self.assertEqual(series.views_count, initial_views + 1)
