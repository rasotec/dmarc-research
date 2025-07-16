from unittest import TestCase
from util import get_org_domain, get_sub_domain

class Test(TestCase):
    def test_get_org_domain(self):
        self.assertEqual('example.com', get_org_domain('example.com.'))
        self.assertEqual('example.com', get_org_domain('example.com'))
        self.assertEqual('example.com', get_org_domain('_dmarc.example.com.'))
        self.assertEqual('example.com', get_org_domain('_dmarc.example.com'))
        self.assertEqual('example.com', get_org_domain('some.more.example.com.'))
        self.assertEqual('example.com', get_org_domain('some.more.example.com'))

    def test_get_sub_domain(self):
        self.assertEqual('', get_sub_domain('example.com'))
        self.assertEqual('_dmarc', get_sub_domain('_dmarc.example.com'))
        self.assertEqual('_dmarc.sub', get_sub_domain('_dmarc.sub.example.com'))

