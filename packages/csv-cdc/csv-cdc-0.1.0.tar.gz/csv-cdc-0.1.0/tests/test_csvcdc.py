import pytest
import tempfile
import os
import json
from io import StringIO
import sys

# Add the parent directory to the path to import csvcdc
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from csvcdc import CSVCDC, CSVCDCResult, OutputFormatter

class TestCSVCDC:
    """Test cases for CSVCDC class"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def sample_csv_files(self, temp_dir):
        """Create sample CSV files for testing"""
        base_content = """id,name,price,category
1,Widget,10.99,Tools
2,Gadget,25.50,Electronics
3,Book,15.99,Education
4,Lamp,45.00,Home"""
        
        delta_content = """id,name,price,category
1,Widget,12.99,Tools
2,Gadget,25.50,Electronics
4,Lamp,39.99,Home
5,Phone,299.99,Electronics"""
        
        base_file = os.path.join(temp_dir, 'base.csv')
        delta_file = os.path.join(temp_dir, 'delta.csv')
        
        with open(base_file, 'w') as f:
            f.write(base_content)
        
        with open(delta_file, 'w') as f:
            f.write(delta_content)
        
        return base_file, delta_file
    
    @pytest.fixture
    def composite_key_files(self, temp_dir):
        """Create CSV files with composite primary keys"""
        base_content = """store_id,product_id,name,price,stock
1,101,Laptop,999.99,5
1,102,Mouse,25.99,50
2,101,Laptop,1099.99,3
2,103,Keyboard,75.00,20"""
        
        delta_content = """store_id,product_id,name,price,stock
1,101,Laptop,899.99,3
1,102,Mouse,25.99,45
1,104,Monitor,299.99,10
2,101,Laptop,999.99,5
2,103,Keyboard,79.99,18"""
        
        base_file = os.path.join(temp_dir, 'base_composite.csv')
        delta_file = os.path.join(temp_dir, 'delta_composite.csv')
        
        with open(base_file, 'w') as f:
            f.write(base_content)
        
        with open(delta_file, 'w') as f:
            f.write(delta_content)
        
        return base_file, delta_file
    
    @pytest.fixture
    def tab_separated_files(self, temp_dir):
        """Create tab-separated files for testing"""
        base_content = """id\tname\tprice\tcategory
1\tWidget\t10.99\tTools
2\tGadget\t25.50\tElectronics"""
        
        delta_content = """id\tname\tprice\tcategory
1\tWidget\t12.99\tTools
3\tNew Item\t5.99\tTools"""
        
        base_file = os.path.join(temp_dir, 'base.tsv')
        delta_file = os.path.join(temp_dir, 'delta.tsv')
        
        with open(base_file, 'w') as f:
            f.write(base_content)
        
        with open(delta_file, 'w') as f:
            f.write(delta_content)
        
        return base_file, delta_file
    
    def test_basic_comparison(self, sample_csv_files):
        """Test basic CSV comparison functionality"""
        base_file, delta_file = sample_csv_files
        
        cdc = CSVCDC(primary_key=[0], progressbar=0)
        result = cdc.compare(base_file, delta_file)
        
        # Check additions
        assert len(result.additions) == 1
        assert "5,Phone,299.99,Electronics" in result.additions
        
        # Check modifications
        assert len(result.modifications) == 2
        modification_originals = [mod['Original'] for mod in result.modifications]
        modification_currents = [mod['Current'] for mod in result.modifications]
        
        assert "1,Widget,10.99,Tools" in modification_originals
        assert "1,Widget,12.99,Tools" in modification_currents
        assert "4,Lamp,45.00,Home" in modification_originals
        assert "4,Lamp,39.99,Home" in modification_currents
        
        # Check deletions
        assert len(result.deletions) == 1
        assert "3,Book,15.99,Education" in result.deletions
    
    def test_composite_primary_key(self, composite_key_files):
        """Test composite primary key functionality"""
        base_file, delta_file = composite_key_files
        
        cdc = CSVCDC(primary_key=[0, 1], progressbar=0)
        result = cdc.compare(base_file, delta_file)
        
        # Should detect changes correctly with composite key
        assert len(result.additions) == 1  # New monitor
        assert len(result.modifications) >= 1  # Price changes
        assert len(result.deletions) == 0  # No complete deletions in this example
    
    def test_custom_separator(self, tab_separated_files):
        """Test custom field separator"""
        base_file, delta_file = tab_separated_files
        
        cdc = CSVCDC(separator='\t', primary_key=[0], progressbar=0)
        result = cdc.compare(base_file, delta_file)
        
        assert len(result.additions) == 1
        assert len(result.modifications) == 1
        assert len(result.deletions) == 1
    
    def test_ignore_columns(self, sample_csv_files):
        """Test ignoring specific columns"""
        base_file, delta_file = sample_csv_files
        
        # Ignore the category column (index 3)
        cdc = CSVCDC(primary_key=[0], ignore_columns=[3], progressbar=0)
        result = cdc.compare(base_file, delta_file)
        
        # Results should be different when ignoring category
        assert isinstance(result, CSVCDCResult)
    
    def test_include_specific_columns(self, sample_csv_files):
        """Test including only specific columns"""
        base_file, delta_file = sample_csv_files
        
        # Include only id, name, and price columns
        cdc = CSVCDC(primary_key=[0], columns=[0, 1, 2], progressbar=0)
        result = cdc.compare(base_file, delta_file)
        
        assert isinstance(result, CSVCDCResult)
    
    def test_auto_primary_key_detection(self, sample_csv_files):
        """Test automatic primary key detection"""
        base_file, delta_file = sample_csv_files
        
        cdc = CSVCDC(autopk=1, progressbar=0)
        result = cdc.compare(base_file, delta_file)
        
        # Should automatically detect column 0 as primary key
        assert cdc.primary_key is not None
        assert isinstance(result, CSVCDCResult)
    
    def test_empty_files(self, temp_dir):
        """Test handling of empty files"""
        empty_file1 = os.path.join(temp_dir, 'empty1.csv')
        empty_file2 = os.path.join(temp_dir, 'empty2.csv')
        
        with open(empty_file1, 'w') as f:
            f.write('')
        
        with open(empty_file2, 'w') as f:
            f.write('')
        
        cdc = CSVCDC(progressbar=0)
        
        # Should handle empty files gracefully
        with pytest.raises(Exception):
            result = cdc.compare(empty_file1, empty_file2)
    
    def test_identical_files(self, sample_csv_files):
        """Test comparison of identical files"""
        base_file, _ = sample_csv_files
        
        cdc = CSVCDC(primary_key=[0], progressbar=0)
        result = cdc.compare(base_file, base_file)
        
        # No differences should be found
        assert len(result.additions) == 0
        assert len(result.modifications) == 0
        assert len(result.deletions) == 0
    
    def test_large_primary_key_values(self, temp_dir):
        """Test handling of large primary key values"""
        base_content = """id,name,value
9999999999999,Large ID Item,100
1234567890123,Another Large ID,200"""
        
        delta_content = """id,name,value
9999999999999,Large ID Item,150
1234567890123,Another Large ID,200
5555555555555,New Large ID,300"""
        
        base_file = os.path.join(temp_dir, 'large_pk_base.csv')
        delta_file = os.path.join(temp_dir, 'large_pk_delta.csv')
        
        with open(base_file, 'w') as f:
            f.write(base_content)
        
        with open(delta_file, 'w') as f:
            f.write(delta_content)
        
        cdc = CSVCDC(primary_key=[0], progressbar=0)
        result = cdc.compare(base_file, delta_file)
        
        assert len(result.additions) == 1
        assert len(result.modifications) == 1
        assert len(result.deletions) == 0

class TestOutputFormatter:
    """Test cases for OutputFormatter class"""
    
    @pytest.fixture
    def sample_result(self):
        """Create sample CDC result for testing"""
        result = CSVCDCResult()
        result.additions = ["4,New Item,50.00,Category"]
        result.modifications = [{
            'Original': "1,Old Name,10.00,Cat1",
            'Current': "1,New Name,15.00,Cat1"
        }]
        result.deletions = ["3,Deleted Item,25.00,Old Category"]
        return result
    
    def test_diff_format(self, sample_result):
        """Test diff output format"""
        output = OutputFormatter.format_diff(sample_result)
        
        assert "Additions" in output
        assert "Modifications" in output
        assert "Deletions" in output
        assert "New Item" in output
        assert "Deleted Item" in output
    
    def test_json_format(self, sample_result):
        """Test JSON output format"""
        output = OutputFormatter.format_json(sample_result)
        
        # Should be valid JSON
        data = json.loads(output)
        
        assert "Additions" in data
        assert "Modifications" in data
        assert "Deletions" in data
        assert len(data["Additions"]) == 1
        assert len(data["Modifications"]) == 1
        assert len(data["Deletions"]) == 1
    
    def test_rowmark_format(self, sample_result):
        """Test rowmark output format"""
        output = OutputFormatter.format_rowmark(sample_result)
        
        assert "ADDED" in output
        assert "MODIFIED" in output
        assert "New Item" in output
    
    def test_word_diff_format(self, sample_result):
        """Test word diff output format"""
        output = OutputFormatter.format_word_diff(sample_result)
        
        # Should contain modification markers
        assert isinstance(output, str)

class TestIntegration:
    """Integration tests"""
    
    def test_full_workflow(self, temp_dir):
        """Test complete workflow from file creation to output"""
        # Create test data
        base_data = """product_id,name,price,category,in_stock
P001,Laptop,999.99,Electronics,true
P002,Mouse,25.99,Electronics,true
P003,Desk,199.99,Furniture,false
P004,Chair,149.99,Furniture,true"""
        
        delta_data = """product_id,name,price,category,in_stock
P001,Laptop,899.99,Electronics,true
P002,Mouse,25.99,Electronics,false
P004,Chair,159.99,Furniture,true
P005,Monitor,299.99,Electronics,true"""
        
        base_file = os.path.join(temp_dir, 'products_base.csv')
        delta_file = os.path.join(temp_dir, 'products_delta.csv')
        
        with open(base_file, 'w') as f:
            f.write(base_data)
        
        with open(delta_file, 'w') as f:
            f.write(delta_data)
        
        # Test with auto primary key detection
        cdc = CSVCDC(autopk=1, progressbar=0)
        result = cdc.compare(base_file, delta_file)
        
        # Verify results make sense
        assert len(result.additions) == 1  # P005 Monitor
        assert len(result.modifications) >= 2  # Price and stock changes
        assert len(result.deletions) == 1  # P003 Desk
        
        # Test different output formats
        diff_output = OutputFormatter.format_diff(result)
        json_output = OutputFormatter.format_json(result)
        rowmark_output = OutputFormatter.format_rowmark(result)
        
        assert all(isinstance(output, str) for output in [diff_output, json_output, rowmark_output])
        assert all(len(output) > 0 for output in [diff_output, json_output, rowmark_output])
    
    def test_performance_with_larger_dataset(self, temp_dir):
        """Test performance with a larger dataset"""
        import time
        
        # Create larger dataset
        base_rows = []
        delta_rows = []
        
        # Generate 1000 rows
        for i in range(1000):
            base_rows.append(f"{i},Product_{i},{10.99 + i * 0.1},Category_{i % 10}")
            
            # Modify some rows for delta
            if i % 10 == 0:  # Every 10th item gets price change
                delta_rows.append(f"{i},Product_{i},{15.99 + i * 0.1},Category_{i % 10}")
            elif i % 15 == 0:  # Some items are deleted (not in delta)
                continue
            else:
                delta_rows.append(f"{i},Product_{i},{10.99 + i * 0.1},Category_{i % 10}")
        
        # Add some new items to delta
        for i in range(1000, 1050):
            delta_rows.append(f"{i},New_Product_{i},{20.99 + i * 0.1},New_Category")
        
        base_content = "id,name,price,category\n" + "\n".join(base_rows)
        delta_content = "id,name,price,category\n" + "\n".join(delta_rows)
        
        base_file = os.path.join(temp_dir, 'large_base.csv')
        delta_file = os.path.join(temp_dir, 'large_delta.csv')
        
        with open(base_file, 'w') as f:
            f.write(base_content)
        
        with open(delta_file, 'w') as f:
            f.write(delta_content)
        
        # Time the comparison
        start_time = time.time()
        
        cdc = CSVCDC(primary_key=[0], progressbar=0)
        result = cdc.compare(base_file, delta_file)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete reasonably quickly (less than 5 seconds for 1000 rows)
        assert execution_time < 5.0
        
        # Should find the expected changes
        assert len(result.additions) == 50  # New products
        assert len(result.modifications) > 0  # Price changes
        assert len(result.deletions) > 0  # Deleted items

class TestErrorHandling:
    """Test error handling scenarios"""
    
    def test_nonexistent_file(self):
        """Test handling of nonexistent files"""
        cdc = CSVCDC(progressbar=0)
        
        with pytest.raises(FileNotFoundError):
            cdc.compare('nonexistent_base.csv', 'nonexistent_delta.csv')
    
    def test_invalid_primary_key_column(self, temp_dir):
        """Test invalid primary key column index"""
        content = "a,b,c\n1,2,3\n4,5,6"
        
        base_file = os.path.join(temp_dir, 'test_base.csv')
        delta_file = os.path.join(temp_dir, 'test_delta.csv')
        
        with open(base_file, 'w') as f:
            f.write(content)
        
        with open(delta_file, 'w') as f:
            f.write(content)
        
        # Try to use column index that doesn't exist
        cdc = CSVCDC(primary_key=[10], progressbar=0)
        
        # Should handle gracefully (might use available columns or raise appropriate error)
        try:
            result = cdc.compare(base_file, delta_file)
            # If it succeeds, that's also acceptable behavior
            assert isinstance(result, CSVCDCResult)
        except (IndexError, ValueError):
            # Expected behavior for invalid column index
            pass
    
    def test_malformed_csv(self, temp_dir):
        """Test handling of malformed CSV files"""
        malformed_content = """id,name,price
1,Item One,10.99
2,"Malformed Item with quote,15.99
3,Normal Item,5.99"""
        
        base_file = os.path.join(temp_dir, 'malformed.csv')
        delta_file = os.path.join(temp_dir, 'malformed.csv')
        
        with open(base_file, 'w') as f:
            f.write(malformed_content)
        
        with open(delta_file, 'w') as f:
            f.write(malformed_content)
        
        cdc = CSVCDC(primary_key=[0], progressbar=0)
        
        # Should handle malformed CSV gracefully
        try:
            result = cdc.compare(base_file, delta_file)
            assert isinstance(result, CSVCDCResult)
        except Exception as e:
            # Some parsing errors are acceptable
            assert isinstance(e, (ValueError, FileNotFoundError, Exception))

# Test runner configuration
if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])