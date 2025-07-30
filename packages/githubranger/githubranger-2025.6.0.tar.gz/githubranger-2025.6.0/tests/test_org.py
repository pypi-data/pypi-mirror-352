import githubranger as gr


class TestOrg:
    def test_init(self):
        org = gr.Org(name="test_org")
        assert org.name == "test_org"

    def test_repr(self):
        org = gr.Org(name="test_org")
        assert repr(org) == "Org(name='test_org')"
