function Loader() {
    return (
      <h2>Loading...</h2>
    );
  }


  async function CategorySubCategory ({ idPrefix, handleChange }){
      this.state = {selectValue:" "}
      this.handleChange = (e)=>{
          this.state = e.target.value;
      }

      return(
          <div>
          <Category onChange = {this.handleChange}/>
          <Subcategory category = {this.state}/> 
          </div>
      )
  }

  export default asyncReactor(CategorySubCategory, Loader);
  CategorySubCategory.propTypes = {
    handleChange: PropTypes.func.isRequired,
    idPrefix: PropTypes.string,
  };
  
  CategorySubCategory.defaultProps = {
    idPrefix: '',
  };
    