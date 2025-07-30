from unittest import TestCase
from jennifer.agent.class_selector import MethodSelector


class TestMethodSelector(TestCase):
    def test_parse_profile_item(self):
        text = [
            'bbs.views .set_my_id()Any {1}',
            'bbs.views .set_my_id {name}',
            'bbs.views .set_my_id {1, name}',
            'bbs.views .set_my_id(str,int)Any {1,2}',
            'bbs.views MyClass.set_my_id(str,int)Any {arg,name}',
            'bbs.views',
            'bbs.views .set_my_id()Any',
            'bbs.views .set_my_id(1)Any {1}',
            'bbs.views .set_my_id(1,name)Any {1,2}',
        ]
        expected = [
            [True, 'bbs.views', None, 'set_my_id', [1], [], MethodSelector.ARG_PARAMETER_ONLY],
            [True, 'bbs.views', None, 'set_my_id', [], ['name'], MethodSelector.NAMED_PARAMETER_ONLY],
            [True, 'bbs.views', None, 'set_my_id', [1], ['name'], MethodSelector.BOTH_PARAMETER],
            [True, 'bbs.views', None, 'set_my_id', [], ['str', 'int'], MethodSelector.NAMED_PARAMETER_ONLY],
            [True, 'bbs.views', 'MyClass', 'set_my_id', [], ['arg', 'name'], MethodSelector.NAMED_PARAMETER_ONLY],
            [False, None, None, None, [], [], MethodSelector.ALL_PARAMETER],
            [True, 'bbs.views', None, 'set_my_id', [], [], MethodSelector.ALL_PARAMETER],
            [True, 'bbs.views', None, 'set_my_id', [1], [], MethodSelector.ARG_PARAMETER_ONLY],
            [True, 'bbs.views', None, 'set_my_id', [1], ['name'], MethodSelector.BOTH_PARAMETER],
        ]

        for idx, item in enumerate(text):
            selector = MethodSelector(item)

            expect_result = expected[idx]
            self.assertEqual(selector.is_initialized, expect_result[0], msg=item)
            self.assertEqual(selector.profile_module, expect_result[1], msg=item)
            self.assertEqual(selector.profile_class, expect_result[2], msg=item)
            self.assertEqual(selector.profile_func, expect_result[3], msg=item)
            self.assertEqual(selector.profile_arg_idx, expect_result[4], msg=item)
            self.assertEqual(selector.profile_arg_names, expect_result[5], msg=item)
            self.assertEqual(selector.param_mode, expect_result[6], msg=item)
