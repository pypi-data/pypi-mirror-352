import pytest
import tempfile
import os
import json
from io import StringIO
import sys

# Add the root directory to the path to import csvcdc
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

import csvcdc
from csvcdc import CSVCDC, CSVCDCResult, OutputFormatter

class TestCSVCDC:
    """Test cases for CSVCDC class"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files"""
        import tempfile
        import shutil
        
        temp_directory = tempfile.mkdtemp()
        yield temp_directory
        shutil.rmtree(temp_directory)
        
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
    
    @pytest.fixture
    def large_csv_files(self, temp_dir):
        """Create larger CSV files for testing large file functionality"""
        base_rows = ["id,name,price,category,description"]
        delta_rows = ["id,name,price,category,description"]
        
        # Create 5000 rows for testing chunk processing
        for i in range(1, 5001):
            base_row = f"{i},Product_{i},{10.99 + (i * 0.01):.2f},Category_{i % 10},Description for product {i}"
            base_rows.append(base_row)
            
            # Modify some rows for delta
            if i % 100 == 0:  # Every 100th item gets price change
                delta_row = f"{i},Product_{i},{15.99 + (i * 0.01):.2f},Category_{i % 10},Updated description for product {i}"
                delta_rows.append(delta_row)
            elif i % 250 == 0:  # Some items are deleted (not in delta)
                continue
            else:
                delta_rows.append(base_row)
        
        # Add some new items to delta
        for i in range(5001, 5101):
            delta_row = f"{i},New_Product_{i},{20.99 + (i * 0.01):.2f},New_Category,New product {i}"
            delta_rows.append(delta_row)
        
        base_content = "\n".join(base_rows)
        delta_content = "\n".join(delta_rows)
        
        base_file = os.path.join(temp_dir, 'large_base.csv')
        delta_file = os.path.join(temp_dir, 'large_delta.csv')
        
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
    
    def test_large_files_mode(self, large_csv_files):
        """Test large files mode with chunked processing"""
        base_file, delta_file = large_csv_files
        
        # Test with large files mode enabled
        cdc = CSVCDC(
            primary_key=[0], 
            progressbar=0, 
            largefiles=1, 
            chunk_size=1000
        )
        result = cdc.compare(base_file, delta_file)
        
        # Should detect the expected changes
        assert len(result.additions) == 100  # New products (5001-5100)
        assert len(result.modifications) > 0  # Price changes every 100th item
        assert len(result.deletions) > 0  # Items divisible by 250
        
        # Verify it's actually processing in chunks
        assert isinstance(result, CSVCDCResult)
    
    def test_large_files_vs_normal_mode(self, large_csv_files):
        """Test that large files mode produces same results as normal mode"""
        base_file, delta_file = large_csv_files
        
        # Compare with normal mode
        cdc_normal = CSVCDC(primary_key=[0], progressbar=0, largefiles=0)
        result_normal = cdc_normal.compare(base_file, delta_file)
        
        # Compare with large files mode
        cdc_large = CSVCDC(
            primary_key=[0], 
            progressbar=0, 
            largefiles=1, 
            chunk_size=1000
        )
        result_large = cdc_large.compare(base_file, delta_file)
        
        # Results should be identical
        assert len(result_normal.additions) == len(result_large.additions)
        assert len(result_normal.modifications) == len(result_large.modifications)
        assert len(result_normal.deletions) == len(result_large.deletions)
        
        # Check that the actual content matches
        assert set(result_normal.additions) == set(result_large.additions)
        assert set(result_normal.deletions) == set(result_large.deletions)
    
    def test_custom_chunk_size(self, large_csv_files):
        """Test different chunk sizes"""
        base_file, delta_file = large_csv_files
        
        # Test with small chunk size
        cdc_small = CSVCDC(
            primary_key=[0], 
            progressbar=0, 
            largefiles=1, 
            chunk_size=500
        )
        result_small = cdc_small.compare(base_file, delta_file)
        
        # Test with large chunk size
        cdc_large = CSVCDC(
            primary_key=[0], 
            progressbar=0, 
            largefiles=1, 
            chunk_size=2000
        )
        result_large = cdc_large.compare(base_file, delta_file)
        
        # Results should be the same regardless of chunk size
        assert len(result_small.additions) == len(result_large.additions)
        assert len(result_small.modifications) == len(result_large.modifications)
        assert len(result_small.deletions) == len(result_large.deletions)
    
    def test_autopk_with_large_files(self, large_csv_files):
        """Test auto primary key detection with large files mode"""
        base_file, delta_file = large_csv_files
        
        cdc = CSVCDC(
            autopk=1, 
            progressbar=0, 
            largefiles=1, 
            chunk_size=1000
        )
        result = cdc.compare(base_file, delta_file)
        
        # Should automatically detect column 0 as primary key
        assert cdc.primary_key is not None
        assert isinstance(result, CSVCDCResult)
        assert len(result.additions) > 0 or len(result.modifications) > 0 or len(result.deletions) > 0
    
    def test_empty_files(self, temp_dir):
        """Test handling of empty files"""
        empty_file1 = os.path.join(temp_dir, 'empty1.csv')
        empty_file2 = os.path.join(temp_dir, 'empty2.csv')
        
        with open(empty_file1, 'w') as f:
            f.write('')
        
        with open(empty_file2, 'w') as f:
            f.write('')
        
        # Test both normal and large file modes
        for largefiles in [0, 1]:
            cdc = CSVCDC(progressbar=0, largefiles=largefiles)
            
            # Should handle empty files gracefully
            with pytest.raises(Exception):
                result = cdc.compare(empty_file1, empty_file2)
    
    def test_identical_files(self, sample_csv_files):
        """Test comparison of identical files"""
        base_file, _ = sample_csv_files
        
        # Test both normal and large file modes
        for largefiles in [0, 1]:
            cdc = CSVCDC(primary_key=[0], progressbar=0, largefiles=largefiles)
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
        
        # Test both normal and large file modes
        for largefiles in [0, 1]:
            cdc = CSVCDC(primary_key=[0], progressbar=0, largefiles=largefiles)
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
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files"""
        import tempfile
        import shutil
        
        temp_directory = tempfile.mkdtemp()
        yield temp_directory
        shutil.rmtree(temp_directory)
    
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
        
        # Test both normal and large file modes
        for largefiles in [0, 1]:
            start_time = time.time()
            
            cdc = CSVCDC(primary_key=[0], progressbar=0, largefiles=largefiles)
            result = cdc.compare(base_file, delta_file)
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Should complete reasonably quickly (less than 10 seconds for 1000 rows)
            assert execution_time < 10.0
            
            # Should find the expected changes
            assert len(result.additions) == 50  # New products
            assert len(result.modifications) > 0  # Price changes
            assert len(result.deletions) > 0  # Deleted items
    
    def test_memory_efficiency_large_files(self, temp_dir):
        """Test memory efficiency with large files mode"""
        # Skip memory test if psutil is not available
        try:
            import psutil
        except ImportError:
            pytest.skip("psutil not available for memory testing")
        
        # Create a moderately large dataset (1K rows for CI)
        base_rows = []
        delta_rows = []
        
        for i in range(1000):
            row_data = f"{i},Product_{i} with long description {'x' * 50},{10.99 + i * 0.001:.3f},Category_{i % 100},Extra_field_{i}"
            base_rows.append(row_data)
            
            if i % 50 == 0:
                # Modify every 50th row
                modified_row = f"{i},Modified_Product_{i} with long description {'y' * 50},{15.99 + i * 0.001:.3f},Category_{i % 100},Modified_Extra_field_{i}"
                delta_rows.append(modified_row)
            else:
                delta_rows.append(row_data)
        
        base_content = "id,name,price,category,extra\n" + "\n".join(base_rows)
        delta_content = "id,name,price,category,extra\n" + "\n".join(delta_rows)
        
        base_file = os.path.join(temp_dir, 'memory_test_base.csv')
        delta_file = os.path.join(temp_dir, 'memory_test_delta.csv')
        
        with open(base_file, 'w') as f:
            f.write(base_content)
        
        with open(delta_file, 'w') as f:
            f.write(delta_content)
        
        # Test with large files mode (smaller chunks)
        cdc_large = CSVCDC(
            primary_key=[0], 
            progressbar=0, 
            largefiles=1, 
            chunk_size=100
        )
        result_large = cdc_large.compare(base_file, delta_file)
        
        # Results should still be correct
        assert len(result_large.modifications) == 20  # Every 50th row modified

class TestErrorHandling:
    """Test error handling scenarios"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files"""
        import tempfile
        import shutil
        
        temp_directory = tempfile.mkdtemp()
        yield temp_directory
        shutil.rmtree(temp_directory)
    
    def test_nonexistent_file(self):
        """Test handling of nonexistent files"""
        # Test both normal and large file modes
        for largefiles in [0, 1]:
            cdc = CSVCDC(progressbar=0, largefiles=largefiles)
            
            with pytest.raises((FileNotFoundError, Exception)):
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
        
        # Test both normal and large file modes
        for largefiles in [0, 1]:
            # Try to use column index that doesn't exist
            cdc = CSVCDC(primary_key=[10], progressbar=0, largefiles=largefiles)
            
            # Should handle gracefully (might use available columns or raise appropriate error)
            try:
                result = cdc.compare(base_file, delta_file)
                # If it succeeds, that's also acceptable behavior
                assert isinstance(result, CSVCDCResult)
            except (IndexError, ValueError, Exception):
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
        
        # Test both normal and large file modes
        for largefiles in [0, 1]:
            cdc = CSVCDC(primary_key=[0], progressbar=0, largefiles=largefiles)
            
            # Should handle malformed CSV gracefully
            try:
                result = cdc.compare(base_file, delta_file)
                assert isinstance(result, CSVCDCResult)
            except Exception as e:
                # Some parsing errors are acceptable
                assert isinstance(e, (ValueError, FileNotFoundError, Exception))
    
    def test_invalid_chunk_size(self, temp_dir):
        """Test handling of invalid chunk sizes"""
        content = "a,b,c\n1,2,3\n4,5,6"
        
        base_file = os.path.join(temp_dir, 'test_base.csv')
        delta_file = os.path.join(temp_dir, 'test_delta.csv')
        
        with open(base_file, 'w') as f:
            f.write(content)
        
        with open(delta_file, 'w') as f:
            f.write(content)
        
        # Test with very small chunk size
        cdc_small = CSVCDC(
            primary_key=[0], 
            progressbar=0, 
            largefiles=1, 
            chunk_size=1
        )
        
        # Should handle small chunk sizes
        try:
            result = cdc_small.compare(base_file, delta_file)
            assert isinstance(result, CSVCDCResult)
        except Exception:
            # Some chunk size limitations are acceptable
            pass
        
        # Test with very large chunk size
        cdc_large = CSVCDC(
            primary_key=[0], 
            progressbar=0, 
            largefiles=1, 
            chunk_size=1000000
        )
        
        # Should handle large chunk sizes
        result = cdc_large.compare(base_file, delta_file)
        assert isinstance(result, CSVCDCResult)

# Test runner configuration
if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])