# Fresh test
python3 -m venv test_v2
source test_v2/bin/activate

pip3 install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ visceral==0.1.3

python3 -c "
import visceral
import mcp  # Should work with correct dependencies!
print('✅ Version 0.1.2 with corrected dependencies works!')
"

deactivate
rm -rf test_v2